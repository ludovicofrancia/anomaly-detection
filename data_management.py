import pandas as pd
import duckdb

def load_event_data(csv_path, date_to_check):
    """
    Load and filter event data from a CSV file.

    Args:
        csv_path (str): path to the CSV file.
        date_to_check (str): the date YYYY-MM-DD when we want to perform anomaly detection.

    Returns:
        pd.DataFrame: A filtered dataframe containing events where the event_name
                      matches the specified regex and the date is less than or 
                      equal to `date_to_check`.
    """
    data = pd.read_csv(csv_path)
    
    event_data = duckdb.sql(f"""
            SELECT *
            FROM data
            WHERE regexp_matches(event_name, '^[^(),=0-9<>]+$') --only select valid event names
            AND Date <= '{date_to_check}'
        """).df()

    return event_data

def get_properties_to_check(event_data, date_to_check):
    """
    Get the unique properties associated with a specific date.

    Args:
        event_data (pd.DataFrame): the dataframe containing event data.
        date_to_check (str): the date YYYY-MM-DD when we want to perform anomaly detection.

    Returns:
        list: A list of unique property names for the given date.
    """
    date_to_check_event_data = event_data[pd.to_datetime(event_data["Date"]) == pd.to_datetime(date_to_check)]
    properties= list(date_to_check_event_data["Property"].unique())
    return properties

def add_missing_dates_to_ds_y(ds_y, date_col_name, min_date, max_date, event_count_col_name):
    """
    Ensure the dataframe contains a continuous date range (missing dates are filled with zeros).

    Args:
        ds_y (pd.DataFrame): input dataframe containing columns 'ds' (dates) and 'y' (values).
        date_col_name (str): col name for the dates.
        min_date (str): start of the date range.
        max_date (str): end of the date range.
        event_count_col_name (str): col name for the event count.

    Returns:
        pd.DataFrame: A dataframe with a complete date range and missing dates filled with zeros.
    """
    # Create a date range from min_date to max_date
    date_range = pd.date_range(start=min_date, end=max_date)
    date_range = pd.DataFrame(date_range, columns=['Date'])
    date_range = date_range.sort_values(by='Date', ascending=False)
    
    # Merge the date range with the input dataframe
    df = pd.merge(date_range, ds_y, left_on='Date', right_on=date_col_name, how='left')
    
    # Drop the original date col, rename the new one and sort descending
    df = df.drop(columns=[date_col_name])
    df = df.rename(columns={'Date': date_col_name})
    df = df.sort_values(by=date_col_name, ascending=False)

    # Fill missing values with zeros
    df[event_count_col_name] = df[event_count_col_name].fillna(0)

    return df

def ds_y_from_api_ga4_events_check(ds_y=None, min_date="", max_date=""):
    """
    Aggregate event counts by date for time series analysis.

    Args:
        ds_y (pd.DataFrame): input dataframe containing columns 'ds' (dates) and 'y' (values).
        min_date (str): start of the date range.
        max_date (str): end of the date range.

    Returns:
        pd.DataFrame: A dataframe containing aggregated counts (`y`) per date (`ds`).
    """
    day_to_check = max_date

    # Aggregate event counts by date
    df = duckdb.sql(f"""
            SELECT Date as ds, SUM(event_count) as y 
            FROM ds_y
            WHERE ds <= '{day_to_check}'
            GROUP BY ds
            ORDER BY ds DESC
        """).df()

    # Add missing dates and fill gaps with zero counts
    df['ds'] = pd.to_datetime(df['ds'])
    df = add_missing_dates_to_ds_y(ds_y=df, date_col_name="ds", min_date=min_date, max_date=max_date, event_count_col_name="y")
    
    return df
