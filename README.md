# Anomaly Detection in Practice: A Real Case Study

## Goal

The project focuses on detecting anomalies in time-series event data collected via Google Analytics from four different e-commerce platforms. The goal is to build a program that is able to support the marketing team in monitoring changes in user behavior on the website or tracking system malfunctions. 

## Highlights

- **Data Management**: Data extraction, manipulation, and transformation;
- **Time Series Analysis**: STL Decomposition and Week-Over-Week Comparison;
- **Google Sheet Integration**: Thresholds for Week-Over-Week comparison can be modified by the marketing team through a Google Sheet.



## Approaches to Detecting Anomalies
The time-series event data collected from Google Analytics of the 4 e-commerce platforms are characterized by strong weekly seasonality and an upward trend in the long run. The characteristics of these data led to the choice of using 2 methodologies for anomaly detection: STL Decomposition and Week-Over-Week Comparison. The developed program subjects each time series to both methods and if at least one of the two methods detects an anomaly then this is then reported to the user.
### STL Decomposition
Seasonal-Trend-Loess decomposition (STL decomposition) is a methodology used to decompose a historical series into three main components: trend, seasonality and residuals.

The trend identifies the long-term change in the data without accounting for seasonal fluctuations. Seasonality identifies periodic patterns that repeat over time (e.g., daily, weekly, monthly...). Finally, residuals represent the part of the time series that is not explained by either trend or seasonality. So the residuals contain the information concerning unexpected changes in the time series and these are used by the program to identify any anomalies.

Having established the date on which the presence or absence of an anomaly is to be checked, the program calculates:
- The value of the residual on the day on which the anomaly detection analysis is performed;
- The average of the residuals for the previous 30 days: since residuals represent deviations from expected behavior, their average should tend to zero in the absence of anomalies;
- The standard deviation of the residuals around the mean multiplied by three: having ascertained that the distribution of the residuals approximates the normal distribution we know that about 99.97% of the data falls within three dev.std. of the mean.
- The outlier threshold is equal to the mean of the residuals of the last 30 days + (3 x dev.std. of residuals).

Finally, if the absolute value of the current residual is greater than the calculated anomaly threshold, then the program records and reports an anomaly: if a residual exceeds this threshold then it is highly unlikely to be due to normal variation.
### Week-Over-Week Comparison
In addition to there being a strong weekly seasonality of the time-series event data, the volume of an event on each day of the week is often very close to the volume of the event on the same day in the previous week.

The program using the wow_anomaly_check function performs an analysis of the variation between the volume of the event on the date being checked and the volume of the same event seven days earlier. If this variation in percentage and absolute terms is greater than the thresholds specified by the marketing team in the google sheet file ([here](https://docs.google.com/spreadsheets/d/13ad1oh3NpIt36cEcv__x0m0mIvT2_RQf69linO1sg9I/edit?usp=sharing)) then the program reports and records an anomaly.

## FlowChart of the Program
The developed anomaly detection program can be divided into 5 stages:

1. Data Input;
2. Data Extraction and Preparation;
3. Time Series Extraction;
4. Anomaly Detection;
5. Generation of Results.

**Stage 1 - Data Input.** The user must specify:

- the path to the CSV file containing event data, e.g., “api_ga4_event_data.csv”. 
- a date on which to search for anomalies, ex: “2024-04-10”;
- the link to the Google Sheet file containing the thresholds for the Week-Over-Week Comparison, ex: "https://docs.google.com/spreadsheets/d/13ad1oh3NpIt36cEcv__x0m0mIvT2_RQf69linO1sg9I/export?format=csv".

**Stage 2 - Data Extraction and Preparation.** The program extracts the data contained in the CSV file, identifies the properties to be analyzed, and loads the alert thresholds defined within the google sheet file.

**Stage 3 - Time Series Extraction.** For each possible Property-Platform-event_name combination, the program generates the relevant time series to be subsequently analyzed.

**Stage 4 - Anomaly Detection.** Each time series is then subjected to the two anomaly detection methodologies: STL decomposition and Week-Over-Week Comparison.

**Stage 5 - Generation of Results.** The results of the analyses are displayed in a compact form to the user.
