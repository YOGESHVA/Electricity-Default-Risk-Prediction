
import csv
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Electricity Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #07111f;
        color: #ffffff;
    }

    .main .block-container {
        padding: 1.5rem 2rem 3rem;
        max-width: 100%;
    }

    section[data-testid="stSidebar"] {
        background-color: #0a1728;
        border-right: 1px solid #203b5a;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] p {
        color: #9db1c7;
    }

    h1, h2 {
        color: #ffffff !important;
    }

    h1 {
        font-weight: 800 !important;
    }

    h2 {
        font-weight: 750 !important;
    }

    h3 {
        color: #dce8f4 !important;
    }

    div[data-testid="stMetric"] {
        background-color: #0d1d31;
        border: 1px solid #214363;
        border-radius: 12px;
        padding: 16px;
    }

    div[data-testid="stMetricLabel"] {
        color: #8ea6be !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #0d1d31 !important;
        border-color: #294d70 !important;
        color: #ffffff !important;
    }

    div[data-baseweb="input"] {
        background-color: #0d1d31 !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #214363;
        border-radius: 12px;
        overflow: hidden;
    }

    .stButton button,
    .stFormSubmitButton button {
        background-color: #12365a;
        color: #ffffff;
        border: 1px solid #2b5a82;
        border-radius: 8px;
    }

    hr {
        border-color: #203b5a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# PROJECT PATHS
#
# Expected GitHub structure:
#
# repository/
# ├── app/
# │   └── app.py
# └── data/
#     ├── customers.csv
#     ├── billing_records.csv
#     ├── collection_actions.csv
#     ├── anomaly_detection_results.csv
#     └── default_risk_predictions.csv
# ============================================================

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR.parent / "data"


# ============================================================
# CSV HELPERS
# ============================================================

def clean_columns(df):
    """Remove BOMs, spaces and inconsistent capitalization."""
    df.columns = [
        str(column)
        .replace("\ufeff", "")
        .strip()
        .lower()
        for column in df.columns
    ]

    return df


def read_csv_safely(file_path):
    """Read a CSV and normalize its column names."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    df = pd.read_csv(
        file_path,
        encoding="utf-8-sig",
        skipinitialspace=True,
    )

    # If the file was saved with another delimiter,
    # attempt to detect the delimiter automatically.
    if len(df.columns) == 1:
        try:
            alternative = pd.read_csv(
                file_path,
                encoding="utf-8-sig",
                skipinitialspace=True,
                sep=None,
                engine="python",
            )

            if len(alternative.columns) > 1:
                df = alternative

        except Exception:
            pass

    return clean_columns(df)


def read_collection_actions_csv(file_path):
    """
    Supports the older 8-column collection-action format
    and the newer 9-column format with amount_recovered.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = list(csv.reader(file))

    if not rows:
        raise ValueError(
            "collection_actions.csv is empty."
        )

    header = [
        str(value).replace("\ufeff", "").strip().lower()
        for value in rows[0]
    ]

    expected_columns = [
        "action_id",
        "consumer_id",
        "action_date",
        "action_type",
        "action_outcome",
        "amount_targeted",
        "amount_recovered",
        "officer_id",
        "notes",
    ]

    # Older file: amount_recovered does not exist.
    if (
        len(header) == 8
        and "amount_recovered" not in header
    ):
        header.insert(6, "amount_recovered")
        old_format = True

    elif len(header) == 9:
        old_format = False

    else:
        df = read_csv_safely(file_path)

        if "amount_recovered" not in df.columns:
            df["amount_recovered"] = 0.0

        return df

    fixed_rows = []

    for line_number, original_row in enumerate(
        rows[1:],
        start=2,
    ):
        row = list(original_row)

        # Skip blank rows.
        if not row or all(
            str(value).strip() == ""
            for value in row
        ):
            continue

        if len(row) == 8 and old_format:
            row.insert(6, "0")

        elif len(row) != 9:
            raise ValueError(
                f"Invalid collection_actions.csv row "
                f"{line_number}: expected 8 or 9 fields, "
                f"found {len(row)}."
            )

        fixed_rows.append(row)

    df = pd.DataFrame(
        fixed_rows,
        columns=header,
    )

    # Keep known fields in the correct order.
    if len(df.columns) == 9:
        if not set(expected_columns).issubset(df.columns):
            df.columns = expected_columns

    return clean_columns(df)


def require_columns(df, filename, required_columns):
    """Show a useful error if required columns are missing."""

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"{filename} is missing columns: {missing}. "
            f"Detected columns: {df.columns.tolist()}"
        )


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    customers = read_csv_safely(
        DATA_DIR / "customers.csv"
    )

    billing = read_csv_safely(
        DATA_DIR / "billing_records.csv"
    )

    collection_actions = read_collection_actions_csv(
        DATA_DIR / "collection_actions.csv"
    )

    anomalies = read_csv_safely(
        DATA_DIR / "anomaly_detection_results.csv"
    )

    risk_predictions = read_csv_safely(
        DATA_DIR / "default_risk_predictions.csv"
    )

    # Validate customer data before the dashboard accesses it.
    require_columns(
        customers,
        "customers.csv",
        [
            "consumer_id",
            "category",
            "zone",
            "area",
            "sanctioned_load_kw",
        ],
    )

    require_columns(
        billing,
        "billing_records.csv",
        [
            "consumer_id",
            "billing_month",
            "units_consumed",
            "amount_billed",
            "payment_status",
        ],
    )

    require_columns(
        collection_actions,
        "collection_actions.csv",
        [
            "consumer_id",
            "action_type",
            "action_outcome",
        ],
    )

    require_columns(
        anomalies,
        "anomaly_detection_results.csv",
        ["consumer_id"],
    )

    require_columns(
        risk_predictions,
        "default_risk_predictions.csv",
        [
            "consumer_id",
            "risk_score",
            "risk_level",
        ],
    )

    return (
        customers,
        billing,
        collection_actions,
        anomalies,
        risk_predictions,
    )


try:
    (
        customers,
        billing,
        collection_actions,
        anomalies,
        risk_predictions,
    ) = load_data()

except Exception as error:
    st.error("Could not load the project data.")

    st.write(
        "Expected data folder:",
        str(DATA_DIR),
    )

    st.write("Required CSV files:")

    st.code(
        "customers.csv\n"
        "billing_records.csv\n"
        "collection_actions.csv\n"
        "anomaly_detection_results.csv\n"
        "default_risk_predictions.csv"
    )

    st.error(str(error))
    st.stop()


# ============================================================
# DATA CLEANING
# ============================================================

for dataframe in [
    customers,
    billing,
    collection_actions,
    anomalies,
    risk_predictions,
]:
    clean_columns(dataframe)

    if "consumer_id" in dataframe.columns:
        dataframe["consumer_id"] = (
            dataframe["consumer_id"]
            .astype(str)
            .str.strip()
        )


billing["billing_month"] = pd.to_datetime(
    billing["billing_month"],
    errors="coerce",
)

billing["payment_status"] = (
    billing["payment_status"]
    .astype(str)
    .str.strip()
    .str.title()
)

risk_predictions["risk_level"] = (
    risk_predictions["risk_level"]
    .astype(str)
    .str.strip()
    .str.upper()
)

if "action_outcome" in collection_actions.columns:
    collection_actions["action_outcome"] = (
        collection_actions["action_outcome"]
        .astype(str)
        .str.strip()
        .str.title()
    )

if "amount_recovered" not in collection_actions.columns:
    collection_actions["amount_recovered"] = 0.0

# Convert numerical columns safely.
for dataframe, columns in [
    (
        billing,
        ["units_consumed", "amount_billed"],
    ),
    (
        collection_actions,
        ["amount_targeted", "amount_recovered"],
    ),
    (
        risk_predictions,
        ["risk_score"],
    ),
]:
    for column in columns:
        if column in dataframe.columns:
            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce",
            ).fillna(0)


# ============================================================
# LOGIN SYSTEM
# Demo credentials. Do not use these credentials
# for a production application.
# ============================================================

USERS = {
    "admin01": {
        "password": "admin123",
        "role": "Admin",
    },
    "officer01": {
        "password": "officer123",
        "role": "Collection Officer",
    },
    "field01": {
        "password": "field123",
        "role": "Field Staff",
    },
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
        placeholder="Enter username",
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter password",
    )

    if st.button(
        "🔐 Login",
        use_container_width=True,
    ):

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


# ============================================================
# ROLE-BASED NAVIGATION
# ============================================================

current_username = st.session_state.get(
    "username",
    "",
)

current_role = st.session_state.get(
    "role",
    "",
)

if current_role == "Admin":

    available_pages = [
        "📊 Risk Intelligence",
        "🔎 Customer Investigation",
        "🚨 Collection & Anomaly",
        "🤖 Risk Prediction",
    ]

elif current_role == "Collection Officer":

    available_pages = [
        "📊 Risk Intelligence",
        "🔎 Customer Investigation",
        "🚨 Collection & Anomaly",
    ]

elif current_role == "Field Staff":

    available_pages = [
        "🔎 Customer Investigation",
        "🚨 Collection & Anomaly",
    ]

else:
    available_pages = ["📊 Risk Intelligence"]


# ============================================================
# SIDEBAR
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
        label_visibility="collapsed",
    )

    st.divider()

    st.caption(
        "Predict → Detect → Investigate → Act → Measure"
    )

    if st.button(
        "🚪 Logout",
        use_container_width=True,
    ):
        st.session_state["logged_in"] = False
        st.session_state.pop("username", None)
        st.session_state.pop("role", None)
        st.rerun()


# ============================================================
# TOP HEADER
# ============================================================

st.title("⚡ ELECTRICITY COMMAND CENTER")

st.caption(
    "Electricity Consumption, Billing & Default Risk Analytics"
)

st.info(
    "Predict → Detect → Investigate → Act → Measure"
)

st.divider()


# ============================================================
# PAGE 1: RISK INTELLIGENCE
# ============================================================

def show_risk_intelligence():

    st.header("📊 Electricity Risk Intelligence")

    st.caption(
        "Monitor electricity consumption, billing, "
        "payment behavior and revenue risk."
    )

    # KPI calculations
    total_customers = customers["consumer_id"].nunique()

    total_consumption = billing["units_consumed"].sum()

    total_billing = billing["amount_billed"].sum()

    unpaid_data = billing[
        billing["payment_status"] == "Unpaid"
    ]

    unpaid_customers = unpaid_data[
        "consumer_id"
    ].nunique()

    revenue_at_risk = unpaid_data[
        "amount_billed"
    ].sum()

    # KPI cards
    st.subheader("📌 Key Performance Indicators")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "👥 Total Customers",
        f"{total_customers:,}",
    )

    col2.metric(
        "⚡ Total Consumption",
        f"{total_consumption:,.0f}",
    )

    col3.metric(
        "💰 Total Billing",
        f"₹{total_billing:,.0f}",
    )

    col4.metric(
        "⚠️ Unpaid Customers",
        f"{unpaid_customers:,}",
    )

    col5.metric(
        "🚨 Revenue at Risk",
        f"₹{revenue_at_risk:,.0f}",
    )

    # Filters
    st.subheader("🔎 Dashboard Filters")

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        zones = ["All"] + sorted(
            customers["zone"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_zone = st.selectbox("Zone", zones)

    with filter_col2:
        categories = ["All"] + sorted(
            customers["category"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_category = st.selectbox(
            "Category",
            categories,
        )

    with filter_col3:
        month_values = (
            billing["billing_month"]
            .dropna()
            .sort_values()
            .dt.strftime("%Y-%m")
            .unique()
            .tolist()
        )

        selected_month = st.selectbox(
            "Billing Month",
            ["All"] + month_values,
        )

    # Apply customer filters
    filtered_customers = customers.copy()

    if selected_zone != "All":
        filtered_customers = filtered_customers[
            filtered_customers["zone"].astype(str)
            == selected_zone
        ]

    if selected_category != "All":
        filtered_customers = filtered_customers[
            filtered_customers["category"].astype(str)
            == selected_category
        ]

    filtered_billing = billing.merge(
        filtered_customers[["consumer_id"]].drop_duplicates(),
        on="consumer_id",
        how="inner",
    )

    if selected_month != "All":
        filtered_billing = filtered_billing[
            filtered_billing["billing_month"].dt.strftime("%Y-%m")
            == selected_month
        ]

    st.divider()

    # Monthly consumption
    st.subheader("📈 Monthly Electricity Consumption")

    monthly_consumption = (
        filtered_billing
        .groupby("billing_month")["units_consumed"]
        .sum()
        .sort_index()
    )

    if not monthly_consumption.empty:
        st.line_chart(
            monthly_consumption,
            use_container_width=True,
        )
    else:
        st.warning(
            "No data available for the selected filters."
        )

    # Monthly billing
    st.subheader("💰 Monthly Billing")

    monthly_billing = (
        filtered_billing
        .groupby("billing_month")["amount_billed"]
        .sum()
        .sort_index()
    )

    if not monthly_billing.empty:
        st.line_chart(
            monthly_billing,
            use_container_width=True,
        )

    # Payment and consumption patterns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💳 Payment Status")

        payment_status = (
            filtered_billing["payment_status"]
            .value_counts()
        )

        if not payment_status.empty:
            st.bar_chart(
                payment_status,
                use_container_width=True,
            )

    with col2:
        st.subheader("⚡ Consumption Pattern")

        if "consumption_pattern" in filtered_billing.columns:
            pattern = (
                filtered_billing["consumption_pattern"]
                .astype(str)
                .str.strip()
                .value_counts()
            )

            st.bar_chart(
                pattern,
                use_container_width=True,
            )
        else:
            st.info(
                "No consumption_pattern column is available."
            )

    # Revenue at risk by zone
    st.subheader("🚨 Revenue at Risk by Zone")

    filtered_unpaid = filtered_billing[
        filtered_billing["payment_status"] == "Unpaid"
    ]

    if not filtered_unpaid.empty:

        revenue_zone = (
            filtered_unpaid
            .merge(
                customers[
                    ["consumer_id", "zone"]
                ].drop_duplicates(),
                on="consumer_id",
                how="left",
            )
            .groupby("zone")["amount_billed"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            revenue_zone,
            use_container_width=True,
        )

    else:
        st.info(
            "No unpaid bills found for the selected filters."
        )


# ============================================================
# PAGE 2: CUSTOMER INVESTIGATION
# ============================================================

def show_customer_investigation():

    st.header("🔎 Customer Investigation")

    st.caption(
        "Customer 360° — Consumption • Billing • Payment • Anomalies"
    )

    customer_list = (
        customers["consumer_id"]
        .dropna()
        .astype(str)
        .sort_values()
        .unique()
        .tolist()
    )

    if not customer_list:
        st.warning("No customers are available.")
        return

    selected_customer = st.selectbox(
        "🔎 Select Consumer ID",
        customer_list,
    )

    customer_data = customers[
        customers["consumer_id"].astype(str)
        == selected_customer
    ]

    if customer_data.empty:
        st.error("Customer not found.")
        return

    customer = customer_data.iloc[0]

    # Customer information
    st.subheader("👤 Customer Information")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Consumer ID",
        str(customer["consumer_id"]),
    )

    col2.metric(
        "Category",
        str(customer.get("category", "N/A")),
    )

    col3.metric(
        "Zone",
        str(customer.get("zone", "N/A")),
    )

    col4.metric(
        "Area",
        str(customer.get("area", "N/A")),
    )

    col5.metric(
        "Sanctioned Load",
        f'{customer.get("sanctioned_load_kw", "N/A")} kW',
    )

    # Billing history
    customer_billing = billing[
        billing["consumer_id"].astype(str)
        == selected_customer
    ].copy()

    unpaid_billing = customer_billing[
        customer_billing["payment_status"] == "Unpaid"
    ]

    unpaid_amount = unpaid_billing["amount_billed"].sum()

    if customer_billing.empty:
        st.warning(
            "No billing records found for this customer."
        )
    else:
        customer_billing = customer_billing.sort_values(
            "billing_month"
        )

        total_units = customer_billing[
            "units_consumed"
        ].sum()

        total_billing = customer_billing[
            "amount_billed"
        ].sum()

        st.subheader("📌 Customer Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "⚡ Total Consumption",
            f"{total_units:,.0f}",
        )

        col2.metric(
            "💰 Total Billing",
            f"₹{total_billing:,.0f}",
        )

        col3.metric(
            "⚠️ Unpaid Bills",
            f"{len(unpaid_billing):,}",
        )

        col4.metric(
            "🚨 Revenue at Risk",
            f"₹{unpaid_amount:,.2f}",
        )

        st.subheader("📈 Monthly Electricity Consumption")

        monthly_consumption = (
            customer_billing
            .set_index("billing_month")["units_consumed"]
            .sort_index()
        )

        st.line_chart(
            monthly_consumption,
            use_container_width=True,
        )

        st.subheader("📋 Customer Billing History")

        billing_columns = [
            column
            for column in [
                "billing_month",
                "units_consumed",
                "amount_billed",
                "payment_status",
                "due_date",
                "payment_date",
                "consumption_pattern",
            ]
            if column in customer_billing.columns
        ]

        st.dataframe(
            customer_billing[billing_columns],
            use_container_width=True,
            hide_index=True,
        )

    # Anomaly history
    st.subheader("⚠️ Customer Anomalies")

    customer_anomalies = anomalies[
        anomalies["consumer_id"]
        .astype(str)
        .str.strip()
        .str.upper()
        == selected_customer.strip().upper()
    ].copy()

    if customer_anomalies.empty:
        st.success(
            "No anomaly records found for this customer."
        )
    else:
        anomaly_columns = [
            column
            for column in [
                "billing_month",
                "units_consumed",
                "previous_units",
                "consumption_change_pct",
                "anomaly_type",
                "amount_billed",
                "payment_status",
            ]
            if column in customer_anomalies.columns
        ]

        st.dataframe(
            customer_anomalies[anomaly_columns],
            use_container_width=True,
            hide_index=True,
        )

    # Collection action form
    st.divider()
    st.subheader("📞 Take Collection Action")

    st.caption(
        "Record the collection action taken for this customer."
    )

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
                    "Field Visit",
                ],
            )

            action_outcome = st.selectbox(
                "Action Outcome",
                [
                    "Pending",
                    "Contacted",
                    "Promised Payment",
                    "Recovered",
                    "No Response",
                ],
            )

            amount_targeted = st.number_input(
                "Amount Targeted (₹)",
                min_value=0.0,
                value=float(unpaid_amount),
                step=100.0,
            )

            amount_recovered = st.number_input(
                "Amount Recovered (₹)",
                min_value=0.0,
                value=0.0,
                step=100.0,
            )

        with col2:
            officer_id = st.text_input(
                "Officer ID",
                placeholder="Example: OFF001",
            )

            notes = st.text_area(
                "Notes",
                placeholder="Enter collection action details...",
            )

        submit_action = st.form_submit_button(
            "📞 Record Collection Action"
        )

        if submit_action:

            if not officer_id.strip():
                st.warning(
                    "Please enter the Officer ID."
                )

            elif amount_recovered > amount_targeted:
                st.warning(
                    "Amount recovered cannot exceed the amount targeted."
                )

            else:
                new_action = pd.DataFrame(
                    [{
                        "action_id": (
                            "ACTION_"
                            + datetime.now().strftime("%Y%m%d%H%M%S")
                        ),
                        "consumer_id": selected_customer,
                        "action_date": datetime.now().strftime("%Y-%m-%d"),
                        "action_type": action_type,
                        "action_outcome": action_outcome,
                        "amount_targeted": amount_targeted,
                        "amount_recovered": amount_recovered,
                        "officer_id": officer_id.strip(),
                        "notes": notes.strip(),
                    }]
                )

                action_file = DATA_DIR / "collection_actions.csv"

                required_columns = [
                    "action_id",
                    "consumer_id",
                    "action_date",
                    "action_type",
                    "action_outcome",
                    "amount_targeted",
                    "amount_recovered",
                    "officer_id",
                    "notes",
                ]

                try:
                    existing_actions = read_collection_actions_csv(
                        action_file
                    )

                    existing_actions = existing_actions.reindex(
                        columns=required_columns,
                        fill_value="",
                    )

                    new_action = new_action.reindex(
                        columns=required_columns
                    )

                    updated_actions = pd.concat(
                        [existing_actions, new_action],
                        ignore_index=True,
                    )

                    updated_actions.to_csv(
                        action_file,
                        index=False,
                    )

                    st.cache_data.clear()

                    st.success(
                        f"Collection action recorded for {selected_customer}."
                    )

                    st.info(
                        f"Action: {action_type} | "
                        f"Outcome: {action_outcome} | "
                        f"Targeted: ₹{amount_targeted:,.2f} | "
                        f"Recovered: ₹{amount_recovered:,.2f}"
                    )

                    st.warning(
                        "Streamlit Cloud local-file changes may not persist "
                        "permanently. Use a database for persistent records."
                    )

                except Exception as error:
                    st.error(
                        f"Could not save collection action: {error}"
                    )

    # Collection history
    st.divider()
    st.subheader("📋 Collection Action History")

    customer_actions = collection_actions[
        collection_actions["consumer_id"]
        .astype(str)
        .str.strip()
        == selected_customer.strip()
    ].copy()

    if customer_actions.empty:
        st.info(
            "No previous collection actions found for this customer."
        )
    else:
        history_columns = [
            column
            for column in [
                "action_date",
                "action_type",
                "action_outcome",
                "amount_targeted",
                "amount_recovered",
                "officer_id",
                "notes",
            ]
            if column in customer_actions.columns
        ]

        if "action_date" in customer_actions.columns:
            customer_actions = customer_actions.sort_values(
                "action_date",
                ascending=False,
            )

        st.dataframe(
            customer_actions[history_columns],
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# PAGE 3: COLLECTION & ANOMALY
# ============================================================

def show_collection_anomaly():

    st.header("🚨 Collection & Anomaly Intelligence")

    st.caption("Act → Recover → Detect")

    unpaid_data = billing[
        billing["payment_status"] == "Unpaid"
    ]

    unpaid_customers = unpaid_data[
        "consumer_id"
    ].nunique()

    revenue_at_risk = unpaid_data[
        "amount_billed"
    ].sum()

    anomaly_cases = len(anomalies)
    collection_action_count = len(collection_actions)

    recovered_actions = (
        (
            collection_actions["action_outcome"]
            == "Recovered"
        ).sum()
        if "action_outcome" in collection_actions.columns
        else 0
    )

    total_targeted = (
        pd.to_numeric(
            collection_actions["amount_targeted"],
            errors="coerce",
        )
        .fillna(0)
        .sum()
        if "amount_targeted" in collection_actions.columns
        else 0.0
    )

    total_recovered = (
        pd.to_numeric(
            collection_actions["amount_recovered"],
            errors="coerce",
        )
        .fillna(0)
        .sum()
        if "amount_recovered" in collection_actions.columns
        else 0.0
    )

    recovery_rate = (
        total_recovered / total_targeted * 100
        if total_targeted > 0
        else 0.0
    )

    # KPIs
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "⚠️ Unpaid Customers",
        f"{unpaid_customers:,}",
    )

    col2.metric(
        "💰 Revenue at Risk",
        f"₹{revenue_at_risk:,.0f}",
    )

    col3.metric(
        "🚨 Anomaly Cases",
        f"{anomaly_cases:,}",
    )

    col4.metric(
        "📞 Collection Actions",
        f"{collection_action_count:,}",
    )

    col5.metric(
        "✅ Recovered Actions",
        f"{recovered_actions:,}",
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🎯 Amount Targeted",
        f"₹{total_targeted:,.0f}",
    )

    col2.metric(
        "💵 Amount Recovered",
        f"₹{total_recovered:,.0f}",
    )

    col3.metric(
        "📈 Recovery Rate",
        f"{recovery_rate:.2f}%",
    )

    # Unpaid customers by zone and collection outcome
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📍 Unpaid Customers by Zone")

        unpaid_zone = (
            unpaid_data
            .merge(
                customers[
                    ["consumer_id", "zone"]
                ].drop_duplicates(),
                on="consumer_id",
                how="left",
            )
            .groupby("zone")["consumer_id"]
            .nunique()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            unpaid_zone,
            use_container_width=True,
        )

    with col2:
        st.subheader("📞 Collection Outcome")

        if "action_outcome" in collection_actions.columns:
            outcome = collection_actions[
                "action_outcome"
            ].value_counts()

            st.bar_chart(
                outcome,
                use_container_width=True,
            )
        else:
            st.warning(
                "action_outcome column not found."
            )

    # Anomaly type and zone
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚠️ Anomaly Type")

        if "anomaly_type" in anomalies.columns:
            anomaly_type = (
                anomalies["anomaly_type"]
                .astype(str)
                .str.strip()
                .value_counts()
            )

            st.bar_chart(
                anomaly_type,
                use_container_width=True,
            )
        else:
            st.info(
                "No anomaly_type column is available."
            )

    with col2:
        st.subheader("📍 Anomaly Cases by Zone")

        anomaly_zone = (
            anomalies
            .merge(
                customers[
                    ["consumer_id", "zone"]
                ].drop_duplicates(),
                on="consumer_id",
                how="left",
            )
            .groupby("zone")["consumer_id"]
            .count()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            anomaly_zone,
            use_container_width=True,
        )

    # Collection actions by zone
    st.subheader("📞 Collection Actions by Zone")

    actions_zone = (
        collection_actions
        .merge(
            customers[
                ["consumer_id", "zone"]
            ].drop_duplicates(),
            on="consumer_id",
            how="left",
        )
        .groupby("zone")["consumer_id"]
        .count()
        .sort_values(ascending=False)
    )

    st.bar_chart(
        actions_zone,
        use_container_width=True,
    )

    # Recent anomalies
    st.subheader("⚠️ Recent Anomaly Records")

    anomaly_columns = [
        column
        for column in [
            "consumer_id",
            "billing_month",
            "units_consumed",
            "previous_units",
            "consumption_change_pct",
            "anomaly_type",
            "amount_billed",
            "payment_status",
        ]
        if column in anomalies.columns
    ]

    st.dataframe(
        anomalies[anomaly_columns].head(100),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# PAGE 4: RISK PREDICTION
# ============================================================

def show_risk_prediction():

    st.header("🤖 Risk Prediction & Model Performance")

    st.caption("Predict → Explain → Prioritize")

    risk_scored_customers = (
        risk_predictions["consumer_id"].nunique()
    )

    high_risk_data = risk_predictions[
        risk_predictions["risk_level"] == "HIGH"
    ]

    high_risk_customers = (
        high_risk_data["consumer_id"].nunique()
    )

    average_risk_score = (
        risk_predictions["risk_score"].mean()
    )

    low_risk = (
        risk_predictions["risk_level"] == "LOW"
    ).sum()

    medium_risk = (
        risk_predictions["risk_level"] == "MEDIUM"
    ).sum()

    # KPI cards
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "🎯 Risk Scored",
        f"{risk_scored_customers:,}",
    )

    col2.metric(
        "🔴 High Risk",
        f"{high_risk_customers:,}",
    )

    col3.metric(
        "📊 Average Risk",
        f"{average_risk_score:.2f}",
    )

    col4.metric(
        "🟢 Low Risk",
        f"{low_risk:,}",
    )

    col5.metric(
        "🟠 Medium Risk",
        f"{medium_risk:,}",
    )

    # Risk distribution and high-risk zone
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Risk Level Distribution")

        risk_distribution = (
            risk_predictions["risk_level"]
            .value_counts()
        )

        st.bar_chart(
            risk_distribution,
            use_container_width=True,
        )

    with col2:
        st.subheader("📍 High-Risk Customers by Zone")

        high_risk_zone = (
            high_risk_data
            .merge(
                customers[
                    ["consumer_id", "zone"]
                ].drop_duplicates(),
                on="consumer_id",
                how="left",
            )
            .groupby("zone")["consumer_id"]
            .nunique()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            high_risk_zone,
            use_container_width=True,
        )

    # Average risk by zone
    st.subheader("📊 Average Risk Score by Zone")

    risk_zone = (
        risk_predictions
        .merge(
            customers[
                ["consumer_id", "zone"]
            ].drop_duplicates(),
            on="consumer_id",
            how="left",
        )
        .groupby("zone")["risk_score"]
        .mean()
        .sort_values(ascending=False)
    )

    st.bar_chart(
        risk_zone,
        use_container_width=True,
    )

    # Risk score distribution
    st.subheader("📈 Risk Score Distribution")

    risk_score_data = pd.DataFrame(
        {
            "Risk Score": risk_predictions["risk_score"]
        }
    )

    st.line_chart(
        risk_score_data,
        use_container_width=True,
    )

    # Model information
    st.subheader("🧠 Model Information")

    model_col1, model_col2, model_col3 = st.columns(3)

    model_col1.metric(
        "Model",
        "Logistic Regression",
    )

    model_col2.metric(
        "Accuracy",
        "71.65%",
    )

    model_col3.metric(
        "Risk Score Range",
        "0–100",
    )

    st.info(
        "The model estimates the probability of customer payment default. "
        "Customers are prioritized using their risk score."
    )

    # Risk prioritization
    st.subheader("👥 Customer Risk Prioritization")

    risk_columns = [
        column
        for column in [
            "consumer_id",
            "risk_score",
            "risk_level",
            "prediction",
            "average_bill",
            "unpaid_count",
            "late_count",
        ]
        if column in risk_predictions.columns
    ]

    risk_table = risk_predictions[
        risk_columns
    ].copy()

    risk_table = risk_table.sort_values(
        "risk_score",
        ascending=False,
    )

    st.dataframe(
        risk_table,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# PAGE ROUTING
# ============================================================

if page == "📊 Risk Intelligence":

    show_risk_intelligence()

elif page == "🔎 Customer Investigation":

    show_customer_investigation()

elif page == "🚨 Collection & Anomaly":

    show_collection_anomaly()

elif page == "🤖 Risk Prediction":

    show_risk_prediction()
