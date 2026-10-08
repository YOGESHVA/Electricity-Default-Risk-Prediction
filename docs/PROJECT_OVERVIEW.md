# Project Overview

## Electricity Consumption Analytics and Bill Default Risk Prediction

### Project Objective

The goal of this project is to build an analytics and decision-support system for electricity billing and payment risk.

The system analyzes customer consumption, billing, and payment history to:

- Identify customers with a high risk of payment default.
- Detect abnormal electricity consumption patterns.
- Analyze unpaid and late payments.
- Identify revenue at risk.
- Support collection teams with customer-level insights.
- Provide dashboards for monitoring billing and default-risk performance.

---

## Business Problem

Electricity distribution companies manage a large number of customers and monthly billing records.

Manual analysis makes it difficult to quickly identify:

- Customers likely to default.
- Areas with high default rates.
- Customers with abnormal consumption.
- Unpaid and late-payment patterns.
- Revenue that may be at risk.

This project provides a data-driven approach to help officers identify these issues earlier.

---

## Project Workflow

The project follows this workflow:

**Predict → Detect → Investigate → Act → Measure**

### 1. Predict

Historical billing and payment information is used to build customer-level features.

A Logistic Regression model predicts the probability of payment default.

### 2. Detect

Monthly consumption is analyzed to identify significant changes in electricity usage.

A rule-based anomaly detection approach flags large month-to-month consumption changes.

### 3. Investigate

Officers can investigate customer information, billing history, payment status, risk level, and anomalies.

### 4. Act

Collection actions can be recorded for customers requiring follow-up.

### 5. Measure

Dashboards are used to monitor:

- Revenue at risk
- Default-risk distribution
- Collection performance
- Recovery performance
- Consumption patterns
- Anomaly cases

---

## Technology Stack

- Python
- Pandas
- NumPy
- Scikit-learn
- MySQL
- SQL
- Power BI
- Streamlit
- GitHub

---

## Main Project Components

### Data Processing

Customer and billing data are processed using Python and Pandas.

### SQL Analysis

SQL is used to answer business questions related to customers, billing, payments, consumption, and revenue.

### Exploratory Data Analysis

EDA is performed to understand:

- Consumption patterns
- Billing trends
- Payment status
- Customer behavior
- Missing values
- Data distributions

### Machine Learning

A Logistic Regression model is used for default-risk prediction.

The model generates a risk probability that is converted into a risk score from 0 to 100.

Risk levels are categorized as:

- LOW
- MEDIUM
- HIGH

### Anomaly Detection

A rule-based month-to-month consumption comparison is used to identify significant consumption changes.

### Power BI

Power BI provides business dashboards for monitoring project KPIs and trends.

### Streamlit

Streamlit provides an interactive application for customer investigation, risk analysis, anomaly review, and collection actions.

---

## Dashboard Pages

### 1. Risk Intelligence

Provides an overview of:

- Total customers
- Total consumption
- Total billing
- Unpaid customers
- Revenue at risk
- Monthly billing and consumption
- Payment status
- Risk by zone

### 2. Customer Investigation

Provides customer-level information including:

- Customer details
- Billing history
- Payment behavior
- Risk score
- Risk level
- Consumption patterns
- Anomaly information

### 3. Collection & Anomaly Intelligence

Focuses on:

- Unpaid customers
- Revenue at risk
- Anomaly cases
- Collection actions
- Recovery performance

### 4. Risk Prediction & Model Performance

Shows:

- Customers scored
- High-risk customers
- Average risk score
- Low/Medium/High risk distribution
- Model performance metrics

---

## User Roles

### Admin

Can access all major project sections.

### Collection Officer

Can review risk intelligence, investigate customers, and manage collection-related activities.

### Field Staff

Can investigate customers and review collection/anomaly information relevant to field activities.

---

## Expected Business Value

The system helps electricity distribution teams move from reactive billing management toward proactive risk management.

It can help teams:

- Prioritize high-risk customers.
- Identify abnormal consumption earlier.
- Focus collection efforts.
- Understand revenue exposure.
- Monitor recovery performance.
- Make data-driven decisions.

---

## Project Repository

The complete project contains:

- Python analysis scripts
- Machine learning code
- SQL queries
- CSV datasets
- Power BI dashboard screenshots
- Streamlit application
- Project documentation
