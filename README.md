© 2024 Ludovico Francia. All rights reserved.
# 🚨 Automated Anomaly Detection for Event Monitoring

**Replacing Manual Monitoring in a Business-Critical Ads Pipeline**

## 🔧 Tech Stack

`Python · Pandas · DuckDB · Time Series Analysis · STL Decomposition · GCP Cloud Functions · Google Analytics`

## Project Overview

**Business Problem**

At Immobiliare.it, user events tracked via Google Analytics are **critical inputs for ads campaigns**.

These events directly affect:

- campaign optimization
- budget allocation
- attribution
- performance measurement

Before this project, a **human analyst manually monitored events every day**, spending **hours** inspecting dashboards to identify drops, spikes, or tracking issues.

As traffic grew to **millions of events per day**, this approach became **unsustainable and risky**.

**My Solution**

I designed and implemented an **automated anomaly detection system** that:

- runs **daily** on millions of events
- replaces manual monitoring
- detects abnormal changes in user behavior or tracking
- alerts teams only when intervention is needed

The system was deployed as **Google Cloud Platform (GCP) Functions** and is fully automated.

**Key Outcomes**

- Eliminated manual daily monitoring
- Faster detection of tracking issues impacting ads
- Increased trust in analytics data used by marketing teams

## 🏢 Business Context

The business operates at large scale:

- multiple platforms (web, app)
- multiple properties
- hundreds of event types
- strong weekly seasonality
- continuous product changes

### Why Events Matter

Events are not just analytics artifacts:

- they **power ads campaigns**
- they determine how budgets are optimized
- they influence automated bidding strategies

If events are wrong or delayed:

- ads decisions are wrong
- budget can be wasted
- performance is misinterpreted

## 🎯 Problem Framing

### Before Automation

- One or more analysts manually:
    - checked dashboards
    - compared metrics day-over-day and week-over-week
    - visually identified anomalies
- The process was:
    - time-consuming
    - subjective
    - not scalable
    - dependent on individual expertise

### Core Problem

> How can we guarantee daily reliability of event data, at scale, without relying on manual checks?
> 

## 📊 Data Description

- **Daily aggregated event counts**
- Dimensions:
    - Property
    - Platform
    - Event name
- Volume:
    - **millions of events per day**
- Characteristics:
    - strong weekly seasonality
    - long-term growth trend
    - highly heterogeneous event volumes

These characteristics made simple threshold-based monitoring ineffective.

## 🛠️ Technical Approach

To reflect real-world constraints, I used a **hybrid anomaly detection strategy**.

### 1️⃣ STL Decomposition (Statistical Method)

**Why**

- Handles seasonality explicitly
- Interpretable
- Robust for operational monitoring

**How**

- Decomposed each time series into:
    - trend
    - seasonality
    - residuals
- Used residuals to detect unexpected deviations
- Applied **dynamic thresholds** to:
    - reduce false positives on low-volume events
    - adapt to changing traffic levels

### 2️⃣ Week-over-Week Comparison (Rule-Based)

Given strong weekly patterns:

- Compared event volume to the **same weekday of the previous week**
- An anomaly is detected only if:
    - percentage change exceeds a threshold **and**
    - absolute change exceeds a threshold

Thresholds are:

- property-specific
- configurable by non-technical users

## ⚙️ System Design & Deployment

### Architecture

- Implemented as **GCP Cloud Functions**
- Executed **daily**
- Fully automated

### Workflow

1. Load daily GA event data
2. Identify properties active on the target date
3. Build time series for each:
    - Property × Platform × Event
4. Run:
    - STL anomaly detection
    - Week-over-Week checks
5. Aggregate anomalies
6. Generate a compact alert message for stakeholders

## 📣 Output & Alerting

Alerts are designed to be:

- concise
- actionable
- low-noise

Example format (with random numbers):

```
Property A
- Web > search_event | WoW: -1,200 (-35%)
- App > lead_submit | WoW: +950 (+42%)
```

This allows teams to:

- immediately investigate
- understand impact
- avoid alert fatigue

## 📈 Business Impact

### Operational Impact

- Removed hours of manual daily monitoring
- Enabled scalable event reliability checks

### Business Impact

- Faster detection of issues affecting ads campaigns
- Reduced risk of budget misallocation
- Increased trust in marketing analytics

## 🚀 What I’d Improve Next

- Persist anomalies for historical analysis
- Group correlated anomalies
- Add severity scoring
- Introduce model-based forecasting for selected KPIs
