import streamlit as st
import pandas as pd
import csv
from pathlib import Path



# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Electricity Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# NO HTML DIVs ARE USED
# ============================================================

st.markdown(
    """
    <style>

    /* Main application */

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


    /* Sidebar */

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


    /* Sidebar radio */

    div[data-testid="stRadio"] label {
        color: #c7d5e3 !important;
        font-size: 14px !important;
    }


    /* Main titles */

    h1 {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px;
    }

    h2 {
        color: #ffffff !important;
        font-weight: 750 !important;
    }

    h3 {
        color: #dce8f4 !important;
        font-weight: 700 !important;
    }


    /* Metric cards */

    div[data-testid="stMetric"] {
        background-color: #0d1d31;
        border: 1px solid #214363;
        border-radius: 14px;
        padding: 18px;
        min-height: 115px;
        box-shadow: none;
    }

    div[data-testid="stMetricLabel"] {
        color: #8ea6be !important;
        font-size: 13px !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 25px !important;
        font-weight: 800 !important;
    }

    div[data-testid="stMetricDelta"] {
        color: #49d597 !important;
    }


    /* Select boxes */

    div[data-baseweb="select"] > div {
        background-color: #0d1d31 !important;
        border-color: #294d70 !important;
        color: #ffffff !important;
    }


    /* Text input */

    div[data-baseweb="input"] {
        background-color: #0d1d31 !important;
    }


    /* Dataframe */

    div[data-testid="stDataFrame"] {
        border: 1px solid #214363;
        border-radius: 12px;
        overflow: hidden;
    }


    /* Buttons */

    .stButton button {
        background-color: #12365a;
        color: #ffffff;
        border: 1px solid #2b5a82;
        border-radius: 8px;
    }

    .stButton button:hover {
        background-color: #17476f;
        color: #ffffff;
        border-color: #3d7cad;
    }


    /* Horizontal line */

    hr {
        border-color: #203b5a;
    }


    /* Info */

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }


    /* Charts spacing */

    div[data-testid="stVerticalBlock"] {
        gap: 0.8rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PROJECT PATH
# ============================================================

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR.parent / "data"


# ============================================================
# LOAD DATA
# ============================================================

def read_collection_actions_csv(file_path):

    """
    Reads collection_actions.csv safely.

    Supports:
    - Old records with 8 columns
    - New records with 9 columns including amount_recovered

    Old records automatically receive amount_recovered = 0.
    """

    rows = []

    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.reader(file)

        for row in reader:
            rows.append(row)

    if not rows:

        raise ValueError(
            "collection_actions.csv is empty."
        )

    header = rows[0]

    # --------------------------------------------------------
    # EXPECTED COLUMN POSITION
    #
    # 0 action_id
    # 1 consumer_id
    # 2 action_date
    # 3 action_type
    # 4 action_outcome
    # 5 amount_targeted
    # 6 amount_recovered
    # 7 officer_id
    # 8 notes
    # --------------------------------------------------------

    # Convert old 8-column header into 9-column header
    if len(header) == 8:

        header.insert(
            6,
            "amount_recovered"
        )

    elif len(header) != 9:

        raise ValueError(
            f"collection_actions.csv header has "
            f"{len(header)} columns. Expected 8 or 9."
        )

    fixed_rows = []

    # --------------------------------------------------------
    # FIX OLD AND NEW DATA ROWS
    # --------------------------------------------------------

    for line_number, row in enumerate(
        rows[1:],
        start=2
    ):

        # Skip completely empty rows
        if not row or all(
            str(value).strip() == ""
            for value in row
        ):
            continue

        # Old record = 8 columns
        if len(row) == 8:

            # Insert amount_recovered after amount_targeted
            row.insert(
                6,
                "0"
            )

        # New record = 9 columns
        elif len(row) == 9:

            pass

        else:

            raise ValueError(
                f"Invalid collection_actions.csv "
                f"row at line {line_number}: "
                f"expected 8 or 9 fields, "
                f"found {len(row)}."
            )

        fixed_rows.append(row)

    collection_actions = pd.DataFrame(
        fixed_rows,
        columns=header
    )

    return collection_actions


@st.cache_data
def load_data():

    # --------------------------------------------------------
    # CUSTOMERS
    # --------------------------------------------------------

    customers = pd.read_csv(
        DATA_DIR / "customers.csv"
    )

    # --------------------------------------------------------
    # BILLING
    # --------------------------------------------------------

    billing = pd.read_csv(
        DATA_DIR / "billing_records.csv"
    )

    # --------------------------------------------------------
    # COLLECTION ACTIONS
    # --------------------------------------------------------

    collection_actions = read_collection_actions_csv(
        DATA_DIR / "collection_actions.csv"
    )

    # --------------------------------------------------------
    # ANOMALIES
    # --------------------------------------------------------

    anomalies = pd.read_csv(
        DATA_DIR / "anomaly_detection_results.csv"
    )

    # --------------------------------------------------------
    # RISK PREDICTIONS
    # --------------------------------------------------------

    risk_predictions = pd.read_csv(
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
# LOAD DATA SAFELY
# ============================================================

try:

    (
        customers,
        billing,
        collection_actions,
        anomalies,
        risk_predictions
    ) = load_data()

except Exception as e:

    st.error("❌ Could not load the project data.")

    st.write(
        "Please check that these files exist inside the data folder:"
    )

    st.code(
        """
customers.csv
billing_records.csv
collection_actions.csv
anomaly_detection_results.csv
default_risk_predictions.csv
        """
    )

    st.error(str(e))

    st.stop()


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

def clean_columns(df):

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    return df


customers = clean_columns(customers)
billing = clean_columns(billing)
collection_actions = clean_columns(collection_actions)
anomalies = clean_columns(anomalies)
risk_predictions = clean_columns(risk_predictions)

# ============================================================
# RECOVERY COLUMN COMPATIBILITY
# ============================================================

if "amount_recovered" not in collection_actions.columns:
    collection_actions["amount_recovered"] = 0.0


# ============================================================
# DATA CLEANING
# ============================================================

if "billing_month" in billing.columns:

    billing["billing_month"] = pd.to_datetime(
        billing["billing_month"],
        errors="coerce"
    )


if "payment_status" in billing.columns:

    billing["payment_status"] = (
        billing["payment_status"]
        .astype(str)
        .str.strip()
        .str.title()
    )


if "risk_level" in risk_predictions.columns:

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


# ============================================================
# LOGIN SYSTEM
# ============================================================

USERS = {
    "admin01": {"password": "admin123", "role": "Admin"},
    "officer01": {"password": "officer123", "role": "Collection Officer"},
    "field01": {"password": "field123", "role": "Field Staff"}
}


def show_login():

    st.title("⚡ Electricity Command Center")
    st.caption(
        "Electricity Consumption, Billing & Default Risk Analytics"
    )

    st.divider()
    st.subheader("🔐 Login")

    username = st.text_input("Username", placeholder="Enter username")
    password = st.text_input("Password", type="password", placeholder="Enter password")

    if st.button("🔐 Login", use_container_width=True):

        if username not in USERS:
            st.error("❌ Username not found.")

        elif USERS[username]["password"] != password:
            st.error("❌ Incorrect password.")

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

current_username = st.session_state.get("username", "")
current_role = st.session_state.get("role", "")

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
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("Predict → Detect → Investigate → Act → Measure")

    if st.button("🚪 Logout", use_container_width=True):
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
# PAGE 1
# RISK INTELLIGENCE
# ============================================================

def show_risk_intelligence():

    st.header("📊 Electricity Risk Intelligence")

    st.caption(
        "Monitor electricity consumption, billing, payment behavior and revenue risk."
    )


    # --------------------------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------------------------

    total_customers = customers[
        "consumer_id"
    ].nunique()


    total_consumption = billing[
        "units_consumed"
    ].sum()


    total_billing = billing[
        "amount_billed"
    ].sum()


    unpaid_data = billing[
        billing["payment_status"] == "Unpaid"
    ]


    unpaid_customers = unpaid_data[
        "consumer_id"
    ].nunique()


    revenue_at_risk = unpaid_data[
        "amount_billed"
    ].sum()


    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    st.subheader("📌 Key Performance Indicators")

    col1, col2, col3, col4, col5 = st.columns(5)


    col1.metric(
        "👥 Total Customers",
        f"{total_customers:,}"
    )


    col2.metric(
        "⚡ Total Consumption",
        f"{total_consumption:,.0f}"
    )


    col3.metric(
        "💰 Total Billing",
        f"₹{total_billing:,.0f}"
    )


    col4.metric(
        "⚠️ Unpaid Customers",
        f"{unpaid_customers:,}"
    )


    col5.metric(
        "🚨 Revenue at Risk",
        f"₹{revenue_at_risk:,.0f}"
    )


    st.write("")


    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    st.subheader("🔎 Dashboard Filters")


    filter_col1, filter_col2, filter_col3 = st.columns(3)


    with filter_col1:

        zones = ["All"]

        zones += sorted(
            customers["zone"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )


        selected_zone = st.selectbox(
            "Zone",
            zones
        )


    with filter_col2:

        categories = ["All"]

        categories += sorted(
            customers["category"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )


        selected_category = st.selectbox(
            "Category",
            categories
        )


    with filter_col3:

        months = ["All"]

        month_values = (
            billing["billing_month"]
            .dropna()
            .sort_values()
            .dt.strftime("%Y-%m")
            .unique()
            .tolist()
        )

        months += month_values


        selected_month = st.selectbox(
            "Billing Month",
            months
        )


    # --------------------------------------------------------
    # FILTER DATA
    # --------------------------------------------------------

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
        filtered_customers[
            ["consumer_id"]
        ],
        on="consumer_id",
        how="inner"
    )


    if selected_month != "All":

        filtered_billing = filtered_billing[
            filtered_billing[
                "billing_month"
            ].dt.strftime("%Y-%m")
            == selected_month
        ]


    st.divider()


    # --------------------------------------------------------
    # MONTHLY CONSUMPTION
    # --------------------------------------------------------

    st.subheader("📈 Monthly Electricity Consumption")


    monthly_consumption = (
        filtered_billing
        .groupby("billing_month")[
            "units_consumed"
        ]
        .sum()
        .sort_index()
    )


    if not monthly_consumption.empty:

        st.line_chart(
            monthly_consumption,
            use_container_width=True
        )

    else:

        st.warning(
            "No data available for the selected filters."
        )


    # --------------------------------------------------------
    # MONTHLY BILLING
    # --------------------------------------------------------

    st.subheader("💰 Monthly Billing")


    monthly_billing = (
        filtered_billing
        .groupby("billing_month")[
            "amount_billed"
        ]
        .sum()
        .sort_index()
    )


    if not monthly_billing.empty:

        st.line_chart(
            monthly_billing,
            use_container_width=True
        )


    # --------------------------------------------------------
    # PAYMENT STATUS + CONSUMPTION PATTERN
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        st.subheader("💳 Payment Status")


        payment_status = (
            filtered_billing[
                "payment_status"
            ]
            .value_counts()
        )


        if not payment_status.empty:

            st.bar_chart(
                payment_status,
                use_container_width=True
            )


    with col2:

        st.subheader("⚡ Consumption Pattern")


        if "consumption_pattern" in filtered_billing.columns:

            pattern = (
                filtered_billing[
                    "consumption_pattern"
                ]
                .astype(str)
                .str.strip()
                .value_counts()
            )


            st.bar_chart(
                pattern,
                use_container_width=True
            )


    # --------------------------------------------------------
    # REVENUE AT RISK BY ZONE
    # --------------------------------------------------------

    st.subheader("🚨 Revenue at Risk by Zone")


    filtered_unpaid = filtered_billing[
        filtered_billing[
            "payment_status"
        ] == "Unpaid"
    ]


    if not filtered_unpaid.empty:

        revenue_zone = (
            filtered_unpaid
            .merge(
                customers[
                    ["consumer_id", "zone"]
                ],
                on="consumer_id",
                how="left"
            )
            .groupby("zone")[
                "amount_billed"
            ]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        st.bar_chart(
            revenue_zone,
            use_container_width=True
        )

    else:

        st.info(
            "No unpaid customers found for the selected filters."
        )


# ============================================================
# PAGE 2
# CUSTOMER INVESTIGATION
# ============================================================

def show_customer_investigation():

    st.header("🔎 Customer Investigation")

    st.caption(
        "Customer 360° — Consumption • Billing • Payment • Anomalies"
    )


    # --------------------------------------------------------
    # CUSTOMER SELECTION
    # --------------------------------------------------------

    customer_list = (
        customers["consumer_id"]
        .dropna()
        .astype(str)
        .sort_values()
        .tolist()
    )


    selected_customer = st.selectbox(
        "🔎 Select Consumer ID",
        customer_list
    )


    customer_data = customers[
        customers[
            "consumer_id"
        ].astype(str)
        == selected_customer
    ]


    if customer_data.empty:

        st.error(
            "Customer not found."
        )

        return


    customer = customer_data.iloc[0]


    # --------------------------------------------------------
    # CUSTOMER INFORMATION
    # --------------------------------------------------------

    st.subheader("👤 Customer Information")


    col1, col2, col3, col4, col5 = st.columns(5)


    col1.metric(
        "Consumer ID",
        str(customer["consumer_id"])
    )


    col2.metric(
        "Category",
        str(customer["category"])
    )


    col3.metric(
        "Zone",
        str(customer["zone"])
    )


    col4.metric(
        "Area",
        str(customer["area"])
    )


    col5.metric(
        "Sanctioned Load",
        f'{customer["sanctioned_load_kw"]} kW'
    )


    # --------------------------------------------------------
    # BILLING
    # --------------------------------------------------------

    customer_billing = billing[
        billing[
            "consumer_id"
        ].astype(str)
        == selected_customer
    ].copy()


    customer_billing = customer_billing.sort_values(
        "billing_month"
    )


    if customer_billing.empty:

        st.warning(
            "No billing records found for this customer."
        )

        return


    # --------------------------------------------------------
    # CUSTOMER KPIs
    # --------------------------------------------------------

    total_units = customer_billing[
        "units_consumed"
    ].sum()


    total_billing = customer_billing[
        "amount_billed"
    ].sum()


    unpaid_billing = customer_billing[
        customer_billing[
            "payment_status"
        ] == "Unpaid"
    ]


    unpaid_count = len(
        unpaid_billing
    )


    unpaid_amount = unpaid_billing[
        "amount_billed"
    ].sum()


    st.subheader("📌 Customer Summary")


    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "⚡ Total Consumption",
        f"{total_units:,.0f}"
    )


    col2.metric(
        "💰 Total Billing",
        f"₹{total_billing:,.0f}"
    )


    col3.metric(
        "⚠️ Unpaid Bills",
        f"{unpaid_count:,}"
    )


    col4.metric(
        "🚨 Revenue at Risk",
        f"₹{unpaid_amount:,.2f}"
    )


    # --------------------------------------------------------
    # CONSUMPTION
    # --------------------------------------------------------

    st.subheader("📈 Monthly Electricity Consumption")


    monthly_consumption = (
        customer_billing
        .set_index(
            "billing_month"
        )[
            "units_consumed"
        ]
        .sort_index()
    )


    st.line_chart(
        monthly_consumption,
        use_container_width=True
    )


    # --------------------------------------------------------
    # BILLING HISTORY
    # --------------------------------------------------------

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
        column
        for column in billing_columns
        if column in customer_billing.columns
    ]


    st.dataframe(
        customer_billing[
            billing_columns
        ],
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # CUSTOMER ANOMALIES
    # --------------------------------------------------------

    st.subheader("⚠️ Customer Anomalies")


    anomaly_data = anomalies.copy()

    anomaly_data["consumer_id"] = (
        anomaly_data["consumer_id"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    customer_anomalies = anomaly_data[
        anomaly_data["consumer_id"]
        == str(selected_customer).strip().upper()
    ].copy()


    if customer_anomalies.empty:

        st.success(
            "No anomaly records found for this customer."
        )

    else:

        anomaly_columns = [
            "billing_month",
            "units_consumed",
            "previous_units",
            "consumption_change_pct",
            "anomaly_type",
            "amount_billed",
            "payment_status"
        ]


        anomaly_columns = [
            column
            for column in anomaly_columns
            if column in customer_anomalies.columns
        ]


        st.dataframe(
            customer_anomalies[
                anomaly_columns
            ],
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # COLLECTION ACTION
    # --------------------------------------------------------

    st.divider()

    st.subheader("📞 Take Collection Action")

    st.caption(
        "Record the action taken by the collection officer for this customer."
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
                value=float(unpaid_amount),
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
                placeholder="Enter collection action details..."
            )

        submit_action = st.form_submit_button(
            "📞 Record Collection Action"
        )

        if submit_action:

            if not officer_id.strip():

                st.warning(
                    "Please enter the Officer ID."
                )

            else:

                from datetime import datetime

                new_action = pd.DataFrame(
                    [{
                        "action_id":
                            "ACTION_" +
                            datetime.now().strftime("%Y%m%d%H%M%S"),

                        "consumer_id":
                            selected_customer,

                        "action_date":
                            datetime.now().strftime("%Y-%m-%d"),

                        "action_type":
                            action_type,

                        "action_outcome":
                            action_outcome,

                        "amount_targeted":
                            amount_targeted,
                        "amount_recovered":
                            amount_recovered,

                        "officer_id":
                            officer_id.strip(),

                        "notes":
                            notes.strip()
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
                    "notes"
                ]

                existing_actions = read_collection_actions_csv(action_file)
                existing_actions = existing_actions.reindex(
                    columns=required_columns,
                    fill_value=""
                )
                new_action = new_action.reindex(
                    columns=required_columns
                )

                updated_actions = pd.concat(
                    [existing_actions, new_action],
                    ignore_index=True
                )

                updated_actions.to_csv(
                    action_file,
                    index=False
                )

                st.cache_data.clear()

                st.success(
                    f"✅ Collection action recorded for {selected_customer}"
                )

                st.info(
                    f"Action: {action_type} | "
                    f"Outcome: {action_outcome} | "
                    f"Amount Targeted: ₹{amount_targeted:,.2f}"
                )
    # --------------------------------------------------------
    # COLLECTION ACTION HISTORY
    # --------------------------------------------------------

    st.divider()

    st.subheader("📋 Collection Action History")

    customer_actions = collection_actions[
        collection_actions["consumer_id"]
        .astype(str)
        .str.strip()
        == str(selected_customer).strip()
    ].copy()

    if customer_actions.empty:

        st.info(
            "No previous collection actions found for this customer."
        )

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
            column
            for column in history_columns
            if column in customer_actions.columns
        ]

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
# PAGE 3
# COLLECTION & ANOMALY
# ============================================================

def show_collection_anomaly():

    st.header("🚨 Collection & Anomaly Intelligence")

    st.caption(
        "Act → Recover → Detect"
    )


    # --------------------------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------------------------

    unpaid_data = billing[
        billing[
            "payment_status"
        ] == "Unpaid"
    ]


    unpaid_customers = unpaid_data[
        "consumer_id"
    ].nunique()


    revenue_at_risk = unpaid_data[
        "amount_billed"
    ].sum()


    anomaly_cases = len(
        anomalies
    )


    collection_action_count = len(
        collection_actions
    )


    if "action_outcome" in collection_actions.columns:

        recovered_actions = (
            collection_actions[
                "action_outcome"
            ] == "Recovered"
        ).sum()

    else:

        recovered_actions = 0


    # --------------------------------------------------------
    # RECOVERY CALCULATIONS
    # --------------------------------------------------------

    total_targeted = 0.0
    total_recovered = 0.0
    recovery_rate = 0.0

    if "amount_targeted" in collection_actions.columns:
        total_targeted = (
            pd.to_numeric(
                collection_actions["amount_targeted"],
                errors="coerce"
            )
            .fillna(0)
            .sum()
        )

    if "amount_recovered" in collection_actions.columns:
        total_recovered = (
            pd.to_numeric(
                collection_actions["amount_recovered"],
                errors="coerce"
            )
            .fillna(0)
            .sum()
        )

    if total_targeted > 0:
        recovery_rate = (
            total_recovered / total_targeted
        ) * 100

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)


    col1.metric(
        "⚠️ Unpaid Customers",
        f"{unpaid_customers:,}"
    )


    col2.metric(
        "💰 Revenue at Risk",
        f"₹{revenue_at_risk:,.0f}"
    )


    col3.metric(
        "🚨 Anomaly Cases",
        f"{anomaly_cases:,}"
    )


    col4.metric(
        "📞 Collection Actions",
        f"{collection_action_count:,}"
    )


    col5.metric(
        "✅ Recovered Actions",
        f"{recovered_actions:,}"
    )

    col6.metric(
        "🎯 Amount Targeted",
        f"₹{total_targeted:,.0f}"
    )

    col7.metric(
        "💵 Amount Recovered",
        f"₹{total_recovered:,.0f}"
    )

    st.metric(
        "📈 Recovery Rate",
        f"{recovery_rate:.2f}%"
    )


    # --------------------------------------------------------
    # UNPAID CUSTOMERS BY ZONE
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        st.subheader(
            "📍 Unpaid Customers by Zone"
        )


        unpaid_zone = (
            unpaid_data
            .merge(
                customers[
                    ["consumer_id", "zone"]
                ],
                on="consumer_id",
                how="left"
            )
            .groupby("zone")[
                "consumer_id"
            ]
            .nunique()
            .sort_values(
                ascending=False
            )
        )


        st.bar_chart(
            unpaid_zone,
            use_container_width=True
        )


    with col2:

        st.subheader(
            "📞 Collection Outcome"
        )


        if "action_outcome" in collection_actions.columns:

            outcome = (
                collection_actions[
                    "action_outcome"
                ]
                .value_counts()
            )


            st.bar_chart(
                outcome,
                use_container_width=True
            )

        else:

            st.warning(
                "action_outcome column not found."
            )


    # --------------------------------------------------------
    # ANOMALY TYPE + ZONE
    # --------------------------------------------------------

    with col1:

        st.subheader(
            "⚠️ Anomaly Type"
        )


        if "anomaly_type" in anomalies.columns:

            anomaly_type = (
                anomalies[
                    "anomaly_type"
                ]
                .astype(str)
                .str.strip()
                .value_counts()
            )


            st.bar_chart(
                anomaly_type,
                use_container_width=True
            )


    with col2:

        st.subheader(
            "📍 Anomaly Cases by Zone"
        )


        anomaly_zone = (
            anomalies
            .merge(
                customers[
                    ["consumer_id", "zone"]
                ],
                on="consumer_id",
                how="left"
            )
            .groupby("zone")[
                "consumer_id"
            ]
            .count()
            .sort_values(
                ascending=False
            )
        )


        st.bar_chart(
            anomaly_zone,
            use_container_width=True
        )


    # --------------------------------------------------------
    # COLLECTION ACTIONS BY ZONE
    # --------------------------------------------------------

    st.subheader(
        "📞 Collection Actions by Zone"
    )


    actions_zone = (
        collection_actions
        .merge(
            customers[
                ["consumer_id", "zone"]
            ],
            on="consumer_id",
            how="left"
        )
        .groupby("zone")[
            "consumer_id"
        ]
        .count()
        .sort_values(
            ascending=False
        )
    )


    st.bar_chart(
        actions_zone,
        use_container_width=True
    )


    # --------------------------------------------------------
    # RECENT ANOMALIES
    # --------------------------------------------------------

    st.subheader(
        "⚠️ Recent Anomaly Records"
    )


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
        column
        for column in anomaly_columns
        if column in anomalies.columns
    ]


    st.dataframe(
        anomalies[
            anomaly_columns
        ].head(100),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PAGE 4
# RISK PREDICTION
# ============================================================

def show_risk_prediction():

    st.header("🤖 Risk Prediction & Model Performance")

    st.caption(
        "Predict → Explain → Prioritize"
    )


    # --------------------------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------------------------

    risk_scored_customers = (
        risk_predictions[
            "consumer_id"
        ].nunique()
    )


    high_risk_customers = (
        risk_predictions[
            risk_predictions[
                "risk_level"
            ] == "HIGH"
        ][
            "consumer_id"
        ].nunique()
    )


    average_risk_score = (
        risk_predictions[
            "risk_score"
        ].mean()
    )


    low_risk = (
        risk_predictions[
            "risk_level"
        ] == "LOW"
    ).sum()


    medium_risk = (
        risk_predictions[
            "risk_level"
        ] == "MEDIUM"
    ).sum()


    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)


    col1.metric(
        "🎯 Risk Scored",
        f"{risk_scored_customers:,}"
    )


    col2.metric(
        "🔴 High Risk",
        f"{high_risk_customers:,}"
    )


    col3.metric(
        "📊 Average Risk",
        f"{average_risk_score:.2f}"
    )


    col4.metric(
        "🟢 Low Risk",
        f"{low_risk:,}"
    )


    col5.metric(
        "🟠 Medium Risk",
        f"{medium_risk:,}"
    )


    # --------------------------------------------------------
    # RISK DISTRIBUTION
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        st.subheader(
            "🎯 Risk Level Distribution"
        )


        risk_distribution = (
            risk_predictions[
                "risk_level"
            ]
            .value_counts()
        )


        st.bar_chart(
            risk_distribution,
            use_container_width=True
        )


    with col2:

        st.subheader(
            "📍 High-Risk Customers by Zone"
        )


        high_risk_data = risk_predictions[
            risk_predictions[
                "risk_level"
            ] == "HIGH"
        ]


        high_risk_zone = (
            high_risk_data
            .merge(
                customers[
                    ["consumer_id", "zone"]
                ],
                on="consumer_id",
                how="left"
            )
            .groupby("zone")[
                "consumer_id"
            ]
            .nunique()
            .sort_values(
                ascending=False
            )
        )


        st.bar_chart(
            high_risk_zone,
            use_container_width=True
        )


    # --------------------------------------------------------
    # AVERAGE RISK BY ZONE
    # --------------------------------------------------------

    st.subheader(
        "📊 Average Risk Score by Zone"
    )


    risk_zone = (
        risk_predictions
        .merge(
            customers[
                ["consumer_id", "zone"]
            ],
            on="consumer_id",
            how="left"
        )
        .groupby("zone")[
            "risk_score"
        ]
        .mean()
        .sort_values(
            ascending=False
        )
    )


    st.bar_chart(
        risk_zone,
        use_container_width=True
    )


    # --------------------------------------------------------
    # RISK SCORE DISTRIBUTION
    # --------------------------------------------------------

    st.subheader(
        "📈 Risk Score Distribution"
    )


    risk_score_data = pd.DataFrame(
        {
            "Risk Score":
            risk_predictions[
                "risk_score"
            ]
        }
    )


    st.line_chart(
        risk_score_data,
        use_container_width=True
    )


    # --------------------------------------------------------
    # MODEL INFORMATION
    # --------------------------------------------------------

    st.subheader(
        "🧠 Model Information"
    )


    model_col1, model_col2, model_col3 = st.columns(3)


    model_col1.metric(
        "Model",
        "Logistic Regression"
    )


    model_col2.metric(
        "Accuracy",
        "71.65%"
    )


    model_col3.metric(
        "Risk Score Range",
        "0 – 100"
    )


    st.info(
        "The model estimates the probability of customer payment default. "
        "Customers are prioritized using their risk score."
    )


    # --------------------------------------------------------
    # RISK PRIORITIZATION
    # --------------------------------------------------------

    st.subheader(
        "👥 Customer Risk Prioritization"
    )


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
        column
        for column in risk_columns
        if column in risk_predictions.columns
    ]


    risk_table = risk_predictions[
        risk_columns
    ].copy()


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
