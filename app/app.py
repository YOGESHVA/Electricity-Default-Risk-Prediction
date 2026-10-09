
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Electricity Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. CUSTOM CSS
# ============================================================

st.markdown("""
<style>
.stApp {
    background-color: #07111f;
    color: #ffffff;
}
.main .block-container {
    padding-top: 1.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
    padding-bottom: 3rem;
    max-width: 100%;
}
section[data-testid="stSidebar"] {
    background-color: #0a1728;
    border-right: 1px solid #203b5a;
}
h1, h2, h3 {
    color: #ffffff !important;
}
div[data-testid="stMetric"] {
    background-color: #0d1d31;
    border: 1px solid #214363;
    border-radius: 14px;
    padding: 18px;
}
div[data-testid="stMetricLabel"] {
    color: #8ea6be !important;
}
div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 800 !important;
}
.stButton button {
    background-color: #12365a;
    color: white;
    border: 1px solid #2b5a82;
    border-radius: 8px;
}
.stButton button:hover {
    background-color: #17476f;
    color: white;
}
hr {
    border-color: #203b5a;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. PROJECT PATHS
# app.py is in app/ and CSV files are in data/
# ============================================================

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
DATA_DIR = PROJECT_DIR / "data"

# ============================================================
# 4. COLUMN CLEANING
# ============================================================

def clean_columns(df):
    df.columns = [
        str(column)
        .replace("\ufeff", "")
        .replace("\xa0", " ")
        .strip()
        .lower()
        for column in df.columns
    ]

    return df


# ============================================================
# 5. SMART CSV READER
# Automatically detects comma or tab separators
# ============================================================

def read_smart_csv(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(
        file_path,
        encoding="utf-8-sig",
        sep=None,
        engine="python"
    )

    return clean_columns(df)


# ============================================================
# 6. COLLECTION ACTIONS CSV READER
# Supports comma/tab separators and 8/9-column files
# ============================================================

def read_collection_actions_csv(file_path):
    df = read_smart_csv(file_path)

    # Standard expected column names
    expected_columns = [
        "action_id",
        "consumer_id",
        "action_date",
        "action_type",
        "action_outcome",
        "amount_targeted",
        "amount_recovered",
        "officer_id",
        "notes"
    ]

    # If the file has eight columns, add amount_recovered
    # as a blank column. This supports older files.
    if len(df.columns) == 8:
        columns = list(df.columns)

        if "amount_recovered" not in columns:
            if "officer_id" in columns:
                insert_position = columns.index("officer_id")
            else:
                insert_position = 6

            df.insert(insert_position, "amount_recovered", 0)

    # Do not silently reinterpret files with unexpected columns
    if len(df.columns) != 9:
        raise ValueError(
            "collection_actions.csv should contain 8 or 9 columns. "
            f"Found {len(df.columns)} columns: {df.columns.tolist()}"
        )

    # Make sure the recovered amount column exists
    if "amount_recovered" not in df.columns:
        df["amount_recovered"] = 0

    # Add any missing optional columns
    for column in expected_columns:
        if column not in df.columns:
            df[column] = ""

    return df


# ============================================================
# 7. LOAD ALL DATA
# ============================================================

@st.cache_data
def load_data():

    customers = read_smart_csv(
        DATA_DIR / "customers.csv"
    )

    billing = read_smart_csv(
        DATA_DIR / "billing_records.csv"
    )

    collection_actions = read_collection_actions_csv(
        DATA_DIR / "collection_actions.csv"
    )

    anomalies = read_smart_csv(
        DATA_DIR / "anomaly_detection_results.csv"
    )

    risk_predictions = read_smart_csv(
        DATA_DIR / "default_risk_predictions.csv"
    )

    return (
        customers,
        billing,
        collection_actions,
        anomalies,
        risk_predictions
    )


# ============================================================
# 8. LOAD DATA SAFELY
# ============================================================

try:
    (
        customers,
        billing,
        collection_actions,
        anomalies,
        risk_predictions
    ) = load_data()

except Exception as error:
    st.error("Unable to load the project data.")
    st.write("Check that all five files exist in the data folder:")
    st.code(
        "data/customers.csv\n"
        "data/billing_records.csv\n"
        "data/collection_actions.csv\n"
        "data/anomaly_detection_results.csv\n"
        "data/default_risk_predictions.csv"
    )
    st.exception(error)
    st.stop()


# ============================================================
# 9. REQUIRED COLUMN VALIDATION
# ============================================================

required_columns = {
    "customers.csv": (
        customers,
        ["consumer_id", "category", "zone", "area"]
    ),
    "billing_records.csv": (
        billing,
        [
            "consumer_id",
            "billing_month",
            "units_consumed",
            "amount_billed",
            "payment_status"
        ]
    ),
    "anomaly_detection_results.csv": (
        anomalies,
        ["consumer_id"]
    ),
    "default_risk_predictions.csv": (
        risk_predictions,
        ["consumer_id", "risk_score", "risk_level"]
    )
}

column_errors = []

for file_name, (dataframe, expected_columns) in required_columns.items():

    missing = [
        column for column in expected_columns
        if column not in dataframe.columns
    ]

    if missing:
        column_errors.append(
            f"{file_name}: missing {missing}. "
            f"Actual columns: {dataframe.columns.tolist()}"
        )

if column_errors:
    st.error("Some CSV files have unexpected column names.")

    for error_message in column_errors:
        st.write(error_message)

    st.info(
        "Check the header row of each CSV file. "
        "The app now detects comma and tab separators automatically."
    )
    st.stop()


# ============================================================
# 10. DATA CLEANING AND TYPE CONVERSION
# ============================================================

if "sanctioned_load_kw" not in customers.columns:
    customers["sanctioned_load_kw"] = 0

billing["billing_month"] = pd.to_datetime(
    billing["billing_month"],
    errors="coerce"
)

for date_column in ["due_date", "payment_date"]:
    if date_column in billing.columns:
        billing[date_column] = pd.to_datetime(
            billing[date_column],
            errors="coerce"
        )

billing["payment_status"] = (
    billing["payment_status"]
    .astype(str)
    .str.strip()
    .str.title()
)

for column in ["units_consumed", "amount_billed"]:
    billing[column] = pd.to_numeric(
        billing[column],
        errors="coerce"
    ).fillna(0)

risk_predictions["risk_level"] = (
    risk_predictions["risk_level"]
    .astype(str)
    .str.strip()
    .str.upper()
)

risk_predictions["risk_score"] = pd.to_numeric(
    risk_predictions["risk_score"],
    errors="coerce"
).fillna(0)

for column in ["amount_targeted", "amount_recovered"]:
    if column in collection_actions.columns:
        collection_actions[column] = pd.to_numeric(
            collection_actions[column],
            errors="coerce"
        ).fillna(0)

if "action_outcome" in collection_actions.columns:
    collection_actions["action_outcome"] = (
        collection_actions["action_outcome"]
        .astype(str)
        .str.strip()
        .str.title()
    )


# ============================================================
# 11. LOGIN SYSTEM
# Demo credentials only; do not use these for real customer data
# ============================================================

USERS = {
    "admin01": {
        "password": "admin123",
        "role": "Admin"
    },
    "officer01": {
        "password": "officer123",
        "role": "Collection Officer"
    },
    "field01": {
        "password": "field123",
        "role": "Field Staff"
    }
}


def show_login():
    st.title("⚡ Electricity Command Center")
    st.caption(
        "Electricity Consumption, Billing & Default Risk Analytics"
    )
    st.divider()
    st.subheader("🔐 Login")

    username = st.text_input(
        "Username",
        placeholder="Enter username"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter password"
    )

    if st.button("🔐 Login", use_container_width=True):

        if username not in USERS:
            st.error("Username not found.")

        elif USERS[username]["password"] != password:
            st.error("Incorrect password.")

        else:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = USERS[username]["role"]
            st.rerun()


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    show_login()
    st.stop()

current_username = st.session_state.get("username", "")
current_role = st.session_state.get("role", "")


# ============================================================
# 12. ROLE-BASED NAVIGATION
# ============================================================

if current_role == "Admin":
    available_pages = [
        "📊 Risk Intelligence",
        "🔎 Customer Investigation",
        "🚨 Collection & Anomaly",
        "🤖 Risk Prediction"
    ]

elif current_role == "Collection Officer":
    available_pages = [
        "📊 Risk Intelligence",
        "🔎 Customer Investigation",
        "🚨 Collection & Anomaly"
    ]

elif current_role == "Field Staff":
    available_pages = [
        "🔎 Customer Investigation",
        "🚨 Collection & Anomaly"
    ]

else:
    available_pages = ["📊 Risk Intelligence"]


# ============================================================
# 13. SIDEBAR
# ============================================================

with st.sidebar:
    st.title("⚡ Command Center")
    st.caption("DATA DETECTIVES")

    st.write(f"**User:** {current_username}")
    st.write(f"**Role:** {current_role}")
    st.divider()
    st.write("### Navigation")

    page = st.radio(
        "Select Page",
        available_pages,
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("Predict → Detect → Investigate → Act → Measure")

    if st.button("🚪 Logout", use_container_width=True):
        for key in ["logged_in", "username", "role"]:
            st.session_state.pop(key, None)
        st.rerun()


st.title("⚡ ELECTRICITY COMMAND CENTER")
st.caption("Electricity Consumption, Billing & Default Risk Analytics")
st.info("Predict → Detect → Investigate → Act → Measure")
st.divider()


# ============================================================
# PAGE 1: RISK INTELLIGENCE
# ============================================================

def show_risk_intelligence():

    st.header("📊 Electricity Risk Intelligence")
    st.caption(
        "Monitor consumption, billing, payment behavior and revenue risk."
    )

    total_customers = customers["consumer_id"].nunique()
    total_consumption = billing["units_consumed"].sum()
    total_billing = billing["amount_billed"].sum()

    unpaid_data = billing[
        billing["payment_status"].str.lower() == "unpaid"
    ].copy()

    unpaid_customers = unpaid_data["consumer_id"].nunique()
    revenue_at_risk = unpaid_data["amount_billed"].sum()

    st.subheader("📌 Key Performance Indicators")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("👥 Total Customers", f"{total_customers:,}")
    col2.metric("⚡ Total Consumption", f"{total_consumption:,.0f}")
    col3.metric("💰 Total Billing", f"₹{total_billing:,.0f}")
    col4.metric("⚠️ Unpaid Customers", f"{unpaid_customers:,}")
    col5.metric("🚨 Revenue at Risk", f"₹{revenue_at_risk:,.0f}")

    st.subheader("🔎 Dashboard Filters")

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        zones = ["All"] + sorted(
            customers["zone"].dropna().astype(str).unique().tolist()
        )
        selected_zone = st.selectbox("Zone", zones)

    with filter_col2:
        categories = ["All"] + sorted(
            customers["category"].dropna().astype(str).unique().tolist()
        )
        selected_category = st.selectbox("Category", categories)

    with filter_col3:
        months = ["All"] + sorted(
            billing["billing_month"]
            .dropna()
            .dt.strftime("%Y-%m")
            .unique()
            .tolist()
        )
        selected_month = st.selectbox("Billing Month", months)

    filtered_customers = customers.copy()

    if selected_zone != "All":
        filtered_customers = filtered_customers[
            filtered_customers["zone"].astype(str) == selected_zone
        ]

    if selected_category != "All":
        filtered_customers = filtered_customers[
            filtered_customers["category"].astype(str)
            == selected_category
        ]

    filtered_billing = billing.merge(
        filtered_customers[["consumer_id"]].drop_duplicates(),
        on="consumer_id",
        how="inner"
    )

    if selected_month != "All":
        filtered_billing = filtered_billing[
            filtered_billing["billing_month"].dt.strftime("%Y-%m")
            == selected_month
        ]

    st.divider()
    st.subheader("📈 Monthly Electricity Consumption")

    monthly_consumption = (
        filtered_billing
        .groupby("billing_month")["units_consumed"]
        .sum()
        .sort_index()
    )

    if not monthly_consumption.empty:
        st.line_chart(monthly_consumption)
    else:
        st.info("No consumption data for these filters.")

    st.subheader("💰 Monthly Billing")

    monthly_billing = (
        filtered_billing
        .groupby("billing_month")["amount_billed"]
        .sum()
        .sort_index()
    )

    if not monthly_billing.empty:
        st.line_chart(monthly_billing)
    else:
        st.info("No billing data for these filters.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💳 Payment Status")

        if not filtered_billing.empty:
            st.bar_chart(
                filtered_billing["payment_status"].value_counts()
            )
        else:
            st.info("No payment data available.")

    with col2:
        st.subheader("⚡ Consumption Pattern")

        if "consumption_pattern" in filtered_billing.columns:
            st.bar_chart(
                filtered_billing["consumption_pattern"]
                .astype(str)
                .str.strip()
                .value_counts()
            )
        else:
            st.info("No consumption pattern column found.")

    st.subheader("🚨 Revenue at Risk by Zone")

    filtered_unpaid = filtered_billing[
        filtered_billing["payment_status"].str.lower() == "unpaid"
    ]

    if not filtered_unpaid.empty:

        revenue_zone = filtered_unpaid.merge(
            customers[["consumer_id", "zone"]].drop_duplicates(),
            on="consumer_id",
            how="left"
        )

        revenue_zone = (
            revenue_zone.groupby("zone")["amount_billed"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(revenue_zone)

    else:
        st.info("No unpaid bills found for these filters.")


# ============================================================
# PAGE 2: CUSTOMER INVESTIGATION
# ============================================================

def show_customer_investigation():

    st.header("🔎 Customer Investigation")
    st.caption(
        "Customer 360° — Consumption • Billing • Payment • Anomalies"
    )

    customer_list = sorted(
        customers["consumer_id"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if not customer_list:
        st.warning("No customer IDs were found.")
        return

    selected_customer = st.selectbox(
        "🔎 Select Consumer ID",
        customer_list
    )

    customer_data = customers[
        customers["consumer_id"].astype(str) == selected_customer
    ]

    if customer_data.empty:
        st.error("Customer not found.")
        return

    customer = customer_data.iloc[0]

    st.subheader("👤 Customer Information")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Consumer ID", str(customer["consumer_id"]))
    col2.metric("Category", str(customer.get("category", "N/A")))
    col3.metric("Zone", str(customer.get("zone", "N/A")))
    col4.metric("Area", str(customer.get("area", "N/A")))
    col5.metric(
        "Sanctioned Load",
        f'{customer.get("sanctioned_load_kw", 0)} kW'
    )

    customer_billing = billing[
        billing["consumer_id"].astype(str) == selected_customer
    ].copy()

    customer_billing = customer_billing.sort_values("billing_month")

    if customer_billing.empty:
        st.warning("No billing records found for this customer.")
    else:
        total_units = customer_billing["units_consumed"].sum()
        total_amount = customer_billing["amount_billed"].sum()

        unpaid_billing = customer_billing[
            customer_billing["payment_status"].str.lower() == "unpaid"
        ]

        unpaid_count = len(unpaid_billing)
        unpaid_amount = unpaid_billing["amount_billed"].sum()

        st.subheader("📌 Customer Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("⚡ Total Consumption", f"{total_units:,.0f}")
        col2.metric("💰 Total Billing", f"₹{total_amount:,.0f}")
        col3.metric("⚠️ Unpaid Bills", f"{unpaid_count:,}")
        col4.metric("🚨 Revenue at Risk", f"₹{unpaid_amount:,.0f}")

        st.subheader("📈 Monthly Electricity Consumption")

        monthly = (
            customer_billing
            .groupby("billing_month")["units_consumed"]
            .sum()
            .sort_index()
        )

        st.line_chart(monthly)

        st.subheader("📋 Customer Billing History")

        billing_columns = [
            "billing_month",
            "units_consumed",
            "amount_billed",
            "payment_status",
            "due_date",
            "payment_date",
            "consumption_pattern"
        ]

        billing_columns = [
            column for column in billing_columns
            if column in customer_billing.columns
        ]

        st.dataframe(
            customer_billing[billing_columns],
            use_container_width=True,
            hide_index=True
        )

    st.subheader("⚠️ Customer Anomalies")

    customer_anomalies = anomalies[
        anomalies["consumer_id"].astype(str).str.strip().str.upper()
        == selected_customer.strip().upper()
    ].copy()

    if customer_anomalies.empty:
        st.success("No anomaly records found for this customer.")
    else:
        anomaly_columns = [
            "consumer_id",
            "billing_month",
            "units_consumed",
            "previous_units",
            "consumption_change_pct",
            "anomaly_type",
            "amount_billed",
            "payment_status"
        ]

        anomaly_columns = [
            column for column in anomaly_columns
            if column in customer_anomalies.columns
        ]

        st.dataframe(
            customer_anomalies[anomaly_columns],
            use_container_width=True,
            hide_index=True
        )

    # Collection action entry form
    st.divider()
    st.subheader("📞 Record Collection Action")

    with st.form("collection_action_form"):

        col1, col2 = st.columns(2)

        with col1:
            action_type = st.selectbox(
                "Action Type",
                [
                    "Phone Call",
                    "SMS",
                    "Payment Reminder",
                    "Notice",
                    "Field Visit"
                ]
            )

            action_outcome = st.selectbox(
                "Action Outcome",
                [
                    "Pending",
                    "Contacted",
                    "Promised Payment",
                    "Recovered",
                    "No Response"
                ]
            )

            amount_targeted = st.number_input(
                "Amount Targeted (₹)",
                min_value=0.0,
                value=0.0,
                step=100.0
            )

            amount_recovered = st.number_input(
                "Amount Recovered (₹)",
                min_value=0.0,
                value=0.0,
                step=100.0
            )

        with col2:
            officer_id = st.text_input(
                "Officer ID",
                placeholder="Example: OFF001"
            )

            notes = st.text_area(
                "Notes",
                placeholder="Enter collection action details"
            )

        submit_action = st.form_submit_button(
            "📞 Record Collection Action"
        )

        if submit_action:

            if not officer_id.strip():
                st.warning("Please enter the Officer ID.")

            else:
                action_file = DATA_DIR / "collection_actions.csv"

                new_action = {
                    "action_id": (
                        "ACTION_"
                        + datetime.now().strftime("%Y%m%d%H%M%S%f")
                    ),
                    "consumer_id": selected_customer,
                    "action_date": datetime.now().strftime("%Y-%m-%d"),
                    "action_type": action_type,
                    "action_outcome": action_outcome,
                    "amount_targeted": amount_targeted,
                    "amount_recovered": amount_recovered,
                    "officer_id": officer_id.strip(),
                    "notes": notes.strip()
                }

                try:
                    existing_actions = read_collection_actions_csv(
                        action_file
                    )

                    updated_actions = pd.concat(
                        [
                            existing_actions,
                            pd.DataFrame([new_action])
                        ],
                        ignore_index=True
                    )

                    updated_actions.to_csv(
                        action_file,
                        index=False
                    )

                    st.cache_data.clear()

                    st.success("Collection action recorded.")
                    st.warning(
                        "Streamlit Cloud may not retain CSV changes "
                        "after a restart or redeployment. Use a database "
                        "for permanent storage."
                    )

                except Exception as error:
                    st.error(
                        f"Could not save the collection action: {error}"
                    )

    st.divider()
    st.subheader("📋 Collection Action History")

    customer_actions = collection_actions[
        collection_actions["consumer_id"].astype(str).str.strip()
        == selected_customer.strip()
    ].copy()

    if customer_actions.empty:
        st.info("No previous collection actions found.")
    else:
        history_columns = [
            "action_date",
            "action_type",
            "action_outcome",
            "amount_targeted",
            "amount_recovered",
            "officer_id",
            "notes"
        ]

        history_columns = [
            column for column in history_columns
            if column in customer_actions.columns
        ]

        if "action_date" in customer_actions.columns:
            customer_actions = customer_actions.sort_values(
                "action_date",
                ascending=False
            )

        st.dataframe(
            customer_actions[history_columns],
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# PAGE 3: COLLECTION & ANOMALY
# ============================================================

def show_collection_anomaly():

    st.header("🚨 Collection & Anomaly Intelligence")
    st.caption("Act → Recover → Detect")

    unpaid_data = billing[
        billing["payment_status"].str.lower() == "unpaid"
    ].copy()

    unpaid_customers = unpaid_data["consumer_id"].nunique()
    revenue_at_risk = unpaid_data["amount_billed"].sum()
    anomaly_count = len(anomalies)
    action_count = len(collection_actions)

    recovered_actions = 0

    if "action_outcome" in collection_actions.columns:
        recovered_actions = (
            collection_actions["action_outcome"].str.lower()
            == "recovered"
        ).sum()

    total_targeted = collection_actions[
        "amount_targeted"
    ].sum()

    total_recovered = collection_actions[
        "amount_recovered"
    ].sum()

    recovery_rate = (
        total_recovered / total_targeted * 100
        if total_targeted > 0
        else 0
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("⚠️ Unpaid Customers", f"{unpaid_customers:,}")
    col2.metric("💰 Revenue at Risk", f"₹{revenue_at_risk:,.0f}")
    col3.metric("🚨 Anomaly Cases", f"{anomaly_count:,}")
    col4.metric("📞 Collection Actions", f"{action_count:,}")
    col5.metric("✅ Recovered Actions", f"{recovered_actions:,}")

    col1, col2, col3 = st.columns(3)

    col1.metric("🎯 Amount Targeted", f"₹{total_targeted:,.0f}")
    col2.metric("💵 Amount Recovered", f"₹{total_recovered:,.0f}")
    col3.metric("📈 Recovery Rate", f"{recovery_rate:.2f}%")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📍 Unpaid Customers by Zone")

        if not unpaid_data.empty:
            unpaid_zone = unpaid_data.merge(
                customers[["consumer_id", "zone"]].drop_duplicates(),
                on="consumer_id",
                how="left"
            )

            unpaid_zone = (
                unpaid_zone.groupby("zone")["consumer_id"]
                .nunique()
                .sort_values(ascending=False)
            )

            st.bar_chart(unpaid_zone)
        else:
            st.info("No unpaid bills found.")

    with col2:
        st.subheader("📞 Collection Outcome")

        st.bar_chart(
            collection_actions["action_outcome"].value_counts()
        )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚠️ Anomaly Type")

        if "anomaly_type" in anomalies.columns:
            st.bar_chart(anomalies["anomaly_type"].value_counts())
        else:
            st.info("No anomaly type data.")

    with col2:
        st.subheader("📍 Anomaly Cases by Zone")

        anomaly_zone = anomalies.merge(
            customers[["consumer_id", "zone"]].drop_duplicates(),
            on="consumer_id",
            how="left"
        )

        anomaly_zone = (
            anomaly_zone.groupby("zone")["consumer_id"]
            .count()
            .sort_values(ascending=False)
        )

        st.bar_chart(anomaly_zone)

    st.subheader("⚠️ Recent Anomaly Records")

    anomaly_columns = [
        "consumer_id",
        "billing_month",
        "units_consumed",
        "previous_units",
        "consumption_change_pct",
        "anomaly_type",
        "amount_billed",
        "payment_status"
    ]

    anomaly_columns = [
        column for column in anomaly_columns
        if column in anomalies.columns
    ]

    st.dataframe(
        anomalies[anomaly_columns].head(100),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PAGE 4: RISK PREDICTION
# ============================================================

def show_risk_prediction():

    st.header("🤖 Risk Prediction & Model Performance")
    st.caption("Predict → Explain → Prioritize")

    risk_scored_customers = risk_predictions["consumer_id"].nunique()

    high_risk_data = risk_predictions[
        risk_predictions["risk_level"] == "HIGH"
    ].copy()

    high_risk_customers = high_risk_data["consumer_id"].nunique()
    average_risk_score = risk_predictions["risk_score"].mean()

    low_risk = (
        risk_predictions["risk_level"] == "LOW"
    ).sum()

    medium_risk = (
        risk_predictions["risk_level"] == "MEDIUM"
    ).sum()

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("🎯 Risk Scored", f"{risk_scored_customers:,}")
    col2.metric("🔴 High Risk", f"{high_risk_customers:,}")
    col3.metric("📊 Average Risk", f"{average_risk_score:.2f}")
    col4.metric("🟢 Low Risk", f"{low_risk:,}")
    col5.metric("🟠 Medium Risk", f"{medium_risk:,}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Risk Level Distribution")

        st.bar_chart(
            risk_predictions["risk_level"].value_counts()
        )

    with col2:
        st.subheader("📍 High-Risk Customers by Zone")

        high_risk_zone = high_risk_data.merge(
            customers[["consumer_id", "zone"]].drop_duplicates(),
            on="consumer_id",
            how="left"
        )

        high_risk_zone = (
            high_risk_zone.groupby("zone")["consumer_id"]
            .nunique()
            .sort_values(ascending=False)
        )

        st.bar_chart(high_risk_zone)

    st.subheader("📊 Average Risk Score by Zone")

    risk_zone = risk_predictions.merge(
        customers[["consumer_id", "zone"]].drop_duplicates(),
        on="consumer_id",
        how="left"
    )

    risk_zone = (
        risk_zone.groupby("zone")["risk_score"]
        .mean()
        .sort_values(ascending=False)
    )

    st.bar_chart(risk_zone)

    st.subheader("📈 Risk Score Distribution")
    st.line_chart(risk_predictions[["risk_score"]])

    st.subheader("🧠 Model Information")

    model_col1, model_col2, model_col3 = st.columns(3)

    model_col1.metric("Model", "Logistic Regression")
    model_col2.metric("Accuracy", "71.65%")
    model_col3.metric("Risk Score Range", "0–100")

    st.info(
        "The dashboard displays the risk scores supplied in "
        "default_risk_predictions.csv. Model accuracy is a displayed "
        "project value, not a newly calculated evaluation."
    )

    st.subheader("👥 Customer Risk Prioritization")

    risk_columns = [
        "consumer_id",
        "risk_score",
        "risk_level",
        "prediction",
        "average_bill",
        "unpaid_count",
        "late_count"
    ]

    risk_columns = [
        column for column in risk_columns
        if column in risk_predictions.columns
    ]

    risk_table = risk_predictions[risk_columns].copy()
    risk_table = risk_table.sort_values(
        "risk_score",
        ascending=False
    )

    st.dataframe(
        risk_table,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 14. PAGE ROUTING
# ============================================================

if page == "📊 Risk Intelligence":
    show_risk_intelligence()

elif page == "🔎 Customer Investigation":
    show_customer_investigation()

elif page == "🚨 Collection & Anomaly":
    show_collection_anomaly()

elif page == "🤖 Risk Prediction":
    show_risk_prediction()
