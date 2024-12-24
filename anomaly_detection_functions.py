from statsmodels.tsa.seasonal import STL
import pandas as pd

def stl_anomaly_check(ds=None, y=None, dynamic_threshold=True, period=14, robust=True, std_parameter=3):
    """
    Perform anomaly detection using STL decomposition on time series data.

    Args:
        ds (list or pd.Series): the datetime index of the time series data.
        y (list or pd.Series): the values of the time series.
        dynamic_threshold (bool): whether to dynamically adjust the anomaly thresholds based on recent data.
        period (int): the seasonal period for STL decomposition.
        robust (bool): use robust fitting to handle outliers during STL decomposition.
        std_parameter (int): multiplier for the standard deviation to define anomaly thresholds.

    Returns:
        dict: Contains the decomposition results, thresholds, anomalies, and a flag indicating if the last day is anomalous.
    """
    df = pd.DataFrame()
    df['y'] = y
    df['ds'] = pd.to_datetime(ds, errors='raise')
    df.set_index('ds', inplace=True)

    # Ensure sufficient data for STL decomposition
    if len(ds) < 30 or len(y) < 30:
        return {"is_last_day_anomalous": False}
    
    try:
        # Perform STL decomposition
        stl = STL(df['y'], period=period, robust=robust)
        stl_fit_output = stl.fit()
    except Exception as e:
        print(f"stl_anomaly_check: Error during STL fitting {e}")
        return False
    
    # Calculate residual statistics
    resid = stl_fit_output.resid
    resid_mu = resid.mean()
    resid_dev = resid.std()

    # Define anomaly thresholds
    abs_threshold = std_parameter * resid_dev
    if dynamic_threshold:
        last_30days_y= df.sort_values(by='ds', ascending=False).head(30)
        last_30days_y_mean = last_30days_y['y'].mean()

        # Adjust thresholds for low activity levels
        if last_30days_y_mean < 500:
            abs_threshold = (((500 - last_30days_y_mean) / 500) + 1) * abs_threshold

        if abs_threshold < 15:
            abs_threshold += 15

    lower_threshold = resid_mu - abs_threshold
    upper_threshold = resid_mu + abs_threshold

    # Find anomalies
    anomalies = df[(resid < lower_threshold) | (resid > upper_threshold)]
    anomalies = anomalies.sort_index(ascending=False)

    #  Check for anomalies in the last day
    is_last_day_anomalous = False
    if not anomalies.empty and (df.index.astype(str).max() in anomalies.index.astype(str)):
        is_last_day_anomalous = True

    return {
        "df": df,
        "trend": stl_fit_output.trend,
        "seasonal": stl_fit_output.seasonal,
        "resid": resid,
        "expected": stl_fit_output.trend + stl_fit_output.seasonal,
        "lower_threshold": lower_threshold,
        "upper_threshold": upper_threshold,
        "anomalies": anomalies,
        "is_last_day_anomalous": is_last_day_anomalous
    }

def wow_anomaly_check(task="", percentage_threshold=10, absolute_threshold=300):
    """
    Perform a week-over-week (WoW) anomaly detection.

    Args:
        task (dict): it contains the time series data (`ds_y_df`) for analysis.
        percentage_threshold (float): the perc change threshold for anomaly detection.
        absolute_threshold (float): the abs change threshold for anomaly detection.

    Returns:
        dict: Indicates if the last day is anomalous or not.
    """
    value_change_WoW = task["ds_y_df"]['y'].iloc[0] - task["ds_y_df"]['y'].iloc[7]

    # What if division by zero
    if task["ds_y_df"]['y'].iloc[7] == 0:
        perc_change_WoW = round((task["ds_y_df"]['y'].iloc[0] - 1) / 1 * 100)
    else:
        perc_change_WoW = round((task["ds_y_df"]['y'].iloc[0] - task["ds_y_df"]['y'].iloc[7]) / task["ds_y_df"]['y'].iloc[7] * 100)

    # Check for anomalies based on percentage and absolute thresholds
    if abs(perc_change_WoW) > percentage_threshold and abs(value_change_WoW) >= absolute_threshold:
        return {"is_last_day_anomalous": True}
    else:
        return {"is_last_day_anomalous": False}
    
def create_anomalies_message(date_to_check="", anomalies_df=False):
    """
    Generate a summary of the detected anomalies.

    Args:
        date_to_check (str): the date YYYY-MM-DD when we want to perform anomaly detection.
        anomalies_df (pd.DataFrame): the dataframe containing detected anomalies.

    Returns:
        str: A formatted string describing anomalies, or a message indicating no anomalies.
    """

    message_text = ""
    dashboard_text = f"\n \n"

    if isinstance(anomalies_df, pd.DataFrame):
        if dashboard_text not in message_text:
            message_text += dashboard_text

        message_text += "Alerting on Property-Platform-event_name: \n"
        if anomalies_df.empty:
            message_text += "- No anomalies detected \n \n"
        else:
            anomalies_df = anomalies_df.sort_values(by=['Property', 'Platform', 'event_name'])
            current_property = None
            for index, row in anomalies_df.iterrows():
                if current_property is None or row['Property'] != current_property:
                    current_property = row['Property']
                    message_text += f"\n>{current_property}\n"
                message_text += f"- {row['Platform']} > {row['event_name']} | WoW: {row['value_change_WoW']} ({'{:,.0f}'.format(row['perc_change_WoW'])}%)\n"
            message_text += "\n \n"

    return message_text