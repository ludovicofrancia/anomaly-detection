import pandas as pd
from data_management import ds_y_from_api_ga4_events_check
from gsheet_utils import get_df_value_i_j, row_mapping, col_mapping
from anomaly_detection_functions import stl_anomaly_check, wow_anomaly_check

def get_tasks_to_check(df=None, properties_to_check=""):
    """
    Generate a list of tasks to check for anomalies based on the provided dataframe.

    Args:
        df (pd.DataFrame): the df containing event parameters, including `Date`, `Property`, `Platform`, and `event_name`.
        properties_to_check (list): the list of properties to include in the anomaly detection.

    Returns:
        list: A list of dictionaries, each representing a task with `Property`, `Platform`, `event_name`,
              and the corresponding time series data (`ds_y_df`).
    """
    
    # Determine the minimum and maximum dates in the dataset
    min_date = pd.to_datetime(df["Date"]).min().strftime('%Y-%m-%d')
    max_date = pd.to_datetime(df["Date"]).max().strftime('%Y-%m-%d')

    tasks = []

    # Iterate over all properties in the dataset
    properties = list(df['Property'].unique())
    for pr in properties:
        if pr not in properties_to_check:
            continue
        
        # Filter data by property
        df_property = df[df['Property'] == pr]
        platforms = list(df_property['Platform'].unique())
        
        # Iterate over platforms within the property
        for pl in platforms:
            df_property_platform = df_property[df_property['Platform'] == pl]
            event_names = list(df_property_platform['event_name'].unique())

            # Iterate over event names within the platform
            for ev in event_names:
                df_property_platform_event = df_property_platform[df_property_platform['event_name'] == ev]
                ds_y_df = ds_y_from_api_ga4_events_check(ds_y=df_property_platform_event, min_date=min_date, max_date=max_date)
                tasks.append({"Property": pr, "Platform": pl, "event_name": ev, "ds_y_df": ds_y_df})             
    return tasks

def check_property_platform_event(table_df= "", properties_to_check= "", thresholds_gsheet= ""):
    """
    Perform anomaly detection on events for specified properties and platforms.

    Args:
        table_df (pd.DataFrame): the df containing all event data.
        properties_to_check (list): the of properties to include in the anomaly detection.
        thresholds_gsheet (pd.DataFrame): the df containing anomaly detection thresholds for the wow_anomaly_check function.

    Returns:
        pd.DataFrame: Dataframe containing details of detected anomalies.
    """
    tasks= get_tasks_to_check(df= table_df, properties_to_check= properties_to_check)
    df_anomalies= pd.DataFrame(columns=['Date', 'Property', 'Platform', 'event_name', 'value_change_WoW', 'perc_change_WoW', 'value_change_DoD', 'perc_change_DoD', 'is_anomalous'])
    anomaly_date = pd.to_datetime(table_df['Date']).max().strftime('%Y-%m-%d')

    events_to_check = len(tasks)
    anomalies_detected = 0

    # Iterate over each task and perform anomaly detection
    for task in tasks:
        try:
            # Check for anomalies using STL decomposition
            stl_check_result = stl_anomaly_check(ds=task["ds_y_df"]["ds"], y=task["ds_y_df"]["y"], dynamic_threshold=True)

            try:
                # Fetch thresholds from the google sheet dataframe for the specific property
                percentage_threshold= get_df_value_i_j(df= thresholds_gsheet, i_row= row_mapping[task["Property"]], j_col= col_mapping["percentage_threshold"])
                absolute_threshold= get_df_value_i_j(df= thresholds_gsheet, i_row= row_mapping[task["Property"]], j_col= col_mapping["absolute_threshold"])
            except:
                print("Error reading 'Anomaly Detection Thresholds Settings' Google Sheet!")

            # Check for anomalies using Week-over-Week (WoW) method
            wow_check_result = wow_anomaly_check(task=task, percentage_threshold= percentage_threshold, absolute_threshold= absolute_threshold)

            # If anomalies are detected, add them to the anomalies dataframe
            if stl_check_result["is_last_day_anomalous"] or wow_check_result["is_last_day_anomalous"]:
                anomalies_detected += 1

                new_record = pd.DataFrame({
                    'Date': anomaly_date,
                    'Property': task["Property"],
                    'Platform': task["Platform"],
                    'event_name': task["event_name"],
                    'value_change_WoW': task["ds_y_df"]['y'].iloc[0] - task["ds_y_df"]['y'].iloc[7],
                    'perc_change_WoW': round((task["ds_y_df"]['y'].iloc[0] - 1) / 1 * 100) if task["ds_y_df"]['y'].iloc[7] == 0 else round((task["ds_y_df"]['y'].iloc[0] - task["ds_y_df"]['y'].iloc[7]) / task["ds_y_df"]['y'].iloc[7] * 100),
                    'value_change_DoD': task["ds_y_df"]['y'].iloc[0] - task["ds_y_df"]['y'].iloc[1],
                    'perc_change_DoD': round((task["ds_y_df"]['y'].iloc[0] - 1) / 1 * 100) if task["ds_y_df"]['y'].iloc[1] == 0 else round((task["ds_y_df"]['y'].iloc[0] - task["ds_y_df"]['y'].iloc[1]) / task["ds_y_df"]['y'].iloc[1] * 100),
                    'is_anomalous': True,
                }, index=[0])
                
                # Append the new record to the anomalies dataframe
                if df_anomalies.empty:
                    df_anomalies = new_record
                else:
                    df_anomalies = pd.concat([df_anomalies, new_record], ignore_index=True)
                
        except Exception as e:
            print(f"Error on {task['Property']} - {task['Platform']} - {task['event_name']}: {e}")
    
    # Summary of the anomaly detection results
    print(f"Anomalies detected: {anomalies_detected}")
    print(f"Events without detected anomalies: {events_to_check}")
    
    return df_anomalies