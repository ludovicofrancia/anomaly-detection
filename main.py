from gsheet_utils import get_all_gsheet_data
from data_management import load_event_data, get_properties_to_check 
from anomaly_detection_functions import create_anomalies_message
from alerting_events import check_property_platform_event

def main(date_to_check= "2024-04-10", event_data_path= "api_ga4_event_data.csv", thresholds_gsheet_link= "https://docs.google.com/spreadsheets/d/13ad1oh3NpIt36cEcv__x0m0mIvT2_RQf69linO1sg9I/export?format=csv"):
    """
    Main function to run the anomaly detection pipeline.

    Args:
        date_to_check (str): the date YYYY-MM-DD for which anomalies should be detected.
        event_data_path (str): the path to the CSV file containing event data.
        thresholds_gsheet_link (str): URL to the Google Sheet containing anomaly detection thresholds in CSV format.

    Steps:
        1. Load event data.
        2. Identify properties to check for anomalies.
        3. Fetch thresholds from the g sheet.
        4. Perform anomaly detection.
        5. Generate a message summarizing detected anomalies.
        6. Print the anomaly message.
    """
    table_df= load_event_data(event_data_path, date_to_check)
    properties_to_check= get_properties_to_check(table_df, date_to_check)
    thresholds_gsheet= get_all_gsheet_data(thresholds_gsheet_link)

    anomalies_df= check_property_platform_event(table_df= table_df, properties_to_check= properties_to_check, thresholds_gsheet= thresholds_gsheet)
    message_text= create_anomalies_message(date_to_check= date_to_check, anomalies_df= anomalies_df)
    print(message_text)

    return