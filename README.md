# ⚡ Electricity Consumption & Bill Default Risk Prediction

An end-to-end data analytics and machine learning project that analyzes electricity consumption, billing behavior, payment defaults, and abnormal consumption patterns.

The project combines **Python, SQL, Power BI, Machine Learning, and Streamlit** to help utility teams identify payment risk, investigate customers, detect anomalies, and prioritize collection activities.

---

## 🎯 Project Overview

Electricity distribution companies manage a large number of customers, monthly bills, consumption records, and payment transactions.

The goal of this project is to build a data-driven solution that can:

* Analyze electricity consumption patterns
* Analyze monthly billing and payment behavior
* Identify unpaid and late payments
* Detect abnormal consumption patterns
* Predict customer default risk
* Identify customers with higher revenue at risk
* Support collection and investigation activities
* Present business insights through interactive dashboards

### Project Story

**Predict → Detect → Investigate → Act → Measure**

---

## 🏗️ Project Workflow

```text
CSV Data
   ↓
Data Preparation
   ↓
Exploratory Data Analysis
   ↓
SQL Business Analysis
   ↓
Anomaly Detection
   ↓
ML Dataset Creation
   ↓
Default Risk Model
   ↓
Risk Predictions
   ↓
Power BI Dashboards
   ↓
Streamlit Application
```

---

## 🛠️ Technologies Used

| Technology   | Purpose                                         |
| ------------ | ----------------------------------------------- |
| Python       | Data preparation, analysis and machine learning |
| Pandas       | Data manipulation and analysis                  |
| NumPy        | Numerical operations                            |
| SQL / MySQL  | Business and customer-level analysis            |
| Power BI     | Interactive dashboards and reporting            |
| Scikit-learn | Default risk prediction                         |
| Streamlit    | Interactive application                         |
| GitHub       | Version control and project portfolio           |

---

# 📊 Project Dashboards

The project contains four major dashboard views.

## 1. ⚡ Risk Intelligence

Provides an overall view of electricity consumption, billing and payment risk.

### Key information

* Total customers
* Total electricity consumption
* Total billing
* Unpaid customers
* Revenue at risk
* Monthly consumption and billing
* Payment status distribution
* Revenue at risk by zone
* Consumption patterns

### Business Question

> Where is the highest financial and payment risk in the customer base?

---

## 2. 🔎 Customer Investigation

Provides a customer-level 360° view.

### Key information

* Consumer ID
* Customer category
* Zone
* Area
* Sanctioned load
* Monthly electricity consumption
* Billing history
* Payment behavior
* Customer revenue at risk

### Business Question

> What is happening with an individual customer's consumption, billing and payment behavior?

---

## 3. 🚨 Collection & Anomaly Intelligence

Combines collection activity with abnormal consumption analysis.

### Key information

* Unpaid customers
* Revenue at risk
* Anomaly cases
* Collection actions
* Collection outcomes
* Amount targeted
* Amount recovered
* Recovery rate
* Anomaly types
* Anomaly cases by zone

### Business Question

> Which customers require collection attention, and where are abnormal consumption patterns occurring?

---

## 4. 🤖 Risk Prediction & Model Performance

Provides the machine learning prediction results.

### Key information

* Risk-scored customers
* High-risk customers
* Average risk score
* Low / Medium / High risk distribution
* High-risk customers by zone
* Average risk score by zone
* Risk score distribution
* Customer risk prioritization

### Business Question

> Which customers should be prioritized before they become payment defaults?

---

# 🤖 Machine Learning

The project uses historical billing and payment behavior to create customer-level features and predict future default risk.

## Feature Engineering

Historical billing data is used to calculate features such as:

* Total bills
* Total units consumed
* Average units consumed
* Average bill amount
* Total bill amount
* Unpaid bill count
* Late bill count
* Unpaid / late payment behavior

The historical period is used to create customer-level features, while a future billing period is used to create the default target.

## Default Target

A customer is treated as a future default when an unpaid payment status occurs during the future target period.

## Model

The project uses **Logistic Regression** for default-risk prediction.

The model produces a probability of default, which is converted into a risk score from **0–100**.

### Risk Classification

| Risk Score | Risk Level |
| ---------: | ---------- |
|       0–39 | LOW        |
|      40–69 | MEDIUM     |
|     70–100 | HIGH       |

### Model Result

The current model achieved approximately **71.65% accuracy** on the evaluation data.

---

# 🚨 Anomaly Detection

The project also identifies unusual electricity consumption behavior.

The anomaly analysis compares customer consumption across billing periods and identifies significant changes such as:

* Consumption spikes
* Consumption drops
* Unusual month-to-month changes

This helps highlight customers that may require further investigation for possible billing issues, unusual usage, or other abnormal patterns.

---

# 🗃️ Dataset

The project uses multiple datasets covering customers, billing, collections, anomalies and risk predictions.

```text
data/
├── customers.csv
├── billing_records.csv
├── collection_actions.csv
├── anomaly_detection_results.csv
└── default_risk_predictions.csv
```

### Customer Data

Contains information such as:

* Consumer ID
* Category
* Sanctioned load
* Zone
* Area

### Billing Data

Contains:

* Consumer ID
* Billing month
* Units consumed
* Amount billed
* Due date
* Payment date
* Payment status
* Consumption pattern

### Collection Data

Contains collection activity and recovery information.

### Anomaly Data

Contains detected abnormal consumption records.

### Risk Prediction Data

Contains the generated customer risk scores and risk levels.

---

# 🐍 Python Analysis

The analysis section contains the project scripts used for:

```text
analysis/
├── billing_eda.py
├── billing_analysis.py
├── customer_analysis.py
├── anomaly_detection.py
├── ml_dataset.py
└── ml/
    └── Train_default_model.py
```

These scripts cover:

* Exploratory data analysis
* Billing analysis
* Customer analysis
* Anomaly detection
* Machine learning dataset preparation
* Default-risk model training

---

# 📈 Business Questions

The project answers practical business questions such as:

1. Which month has the highest electricity consumption?
2. Which month has the highest total billing?
3. What percentage of bills are unpaid?
4. Which customers frequently pay late?
5. Which zone has the highest default risk?
6. Which customer category consumes the most electricity?
7. Which customers show abnormal consumption?
8. How much revenue is currently at risk?
9. Which customers should collection teams prioritize?
10. How effective are collection actions?

---

# 💡 Key Business Value

The solution helps transform raw electricity and billing data into actionable information.

### Instead of only asking:

> "Who has unpaid bills?"

The project helps answer:

> "Who is likely to default, how much revenue is at risk, what unusual behavior is present, and which customers should be prioritized?"

This supports proactive collection and customer investigation.

---

# 📁 Repository Structure

```text
Electricity-Default-Risk-Prediction/
│
├── app/
│   └── app.py
│
├── data/
│   ├── customers.csv
│   ├── billing_records.csv
│   ├── collection_actions.csv
│   ├── anomaly_detection_results.csv
│   └── default_risk_predictions.csv
│
├── analysis/
│   ├── billing_eda.py
│   ├── billing_analysis.py
│   ├── customer_analysis.py
│   ├── anomaly_detection.py
│   ├── ml_dataset.py
│   └── ml/
│       └── Train_default_model.py
│
├── sql/
│   └── analysis_queries.sql
│
├── powerbi/
│   └── dashboard_screenshots/
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

# 🚀 Running the Streamlit Application

Clone the repository:

```bash
git clone https://github.com/YOGESHVA/Electricity-Default-Risk-Prediction.git
```

Move into the project:

```bash
cd Electricity-Default-Risk-Prediction
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the Streamlit application:

```bash
cd app
streamlit run app.py
```

The application provides role-based access for the project prototype.

---

# 👤 User Roles

The Streamlit prototype contains role-based navigation for:

* **Admin**
* **Collection Officer**
* **Field Staff**

Different roles have access to different parts of the application.

> The authentication in this repository is intended for an academic/project prototype and is not production-grade security.

---

# 🤝 AI-Assisted Development

AI tools, including ChatGPT, were used as a learning and development assistant during the project.

### Personally handled

* Data collection and preparation
* Data cleaning and exploration
* EDA
* SQL analysis
* Business-question analysis
* Power BI dashboard creation
* Project validation and testing
* Understanding project requirements

### AI-assisted

* Advanced machine-learning implementation
* Streamlit application development
* Code suggestions and debugging
* Understanding unfamiliar concepts
* Improving project structure

All generated or suggested code was reviewed, adapted and tested as part of the project development process.

---

# 📌 Project Highlights

* **10,000 customers**
* **120,000 billing records**
* Customer-level electricity consumption analysis
* Payment and billing behavior analysis
* Rule-based anomaly detection
* Machine-learning default-risk prediction
* Four Power BI dashboard pages
* Role-based Streamlit application
* Collection and recovery tracking
* Revenue-at-risk analysis

---

# 👨‍💻 Author

**Yogesh**

Aspiring Data Analyst | Python | SQL | Power BI | Machine Learning

Interested in transforming raw data into meaningful business insights and practical data-driven solutions.
