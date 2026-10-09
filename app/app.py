
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
# 2. CUSTOM CSS - DARK THEME + TEXT COLOR FIX
# ============================================================

st.markdown("""
<style>
/* Main application */
.stApp {
    background-color: #07111f;
    color: #ffffff;
}

.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 100%;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0a1728;
    border-right: 1px solid #203b5a;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #ffffff;
}

/* Headings and general text */
h1, h2, h3, h4, h5, h6,
.stApp p,
.stApp li,
.stApp label,
.stApp [data-testid="stMarkdownContainer"] {
    color: #ffffff;
}

/* ============================================================
   TEXT INPUTS: USERNAME, PASSWORD, OFFICER ID, ETC.
   ============================================================ */

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stDateInput input,
.stTimeInput input,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    background-color: #0d1d31 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
    border-color: #294d70 !important;
}

/* Input containers */
div[data-baseweb="input"],
div[data-baseweb="textarea"] {
    background-color: #0d1d31 !important;
}

/* Placeholder text */
.stTextInput input::placeholder,
.stNumberInput input::placeholder,
.stTextArea textarea::placeholder,
div[data-baseweb="input"] input::placeholder,
div[data-baseweb="textarea"] textarea::placeholder {
    color: #aebfd1 !important;
    -webkit-text-fill-color: #aebfd1 !important;
    opacity: 1 !important;
}

/* Form labels */
.stTextInput label,
.stNumberInput label,
.stTextArea label,
.stDateInput label,
.stTimeInput label,
.stSelectbox label,
.stMultiSelect label,
.stRadio label,
.stCheckbox label,
.stSlider label,
.stFileUploader label {
    color: #ffffff !important;
}

/* ============================================================
   DROPDOWNS AND SELECTBOXES
   ============================================================ */

div[data-baseweb="select"] > div {
    background-color: #0d1d31 !important;
    border-color: #294d70 !important;
}

div[data-baseweb="select"] span,
div[data-baseweb="select"] input,
div[data-baseweb="select"] div {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Dropdown option menu */
div[role="listbox"],
div[role="option"] {
    background-color: #0d1d31 !important;
    color: #ffffff !important;
}

div[role="option"]:hover {
    background-color: #214363 !important;
}

/* Radio buttons and checkboxes */
div[data-testid="stRadio"] label,
div[data-testid="stCheckbox"] label {
    color: #ffffff !important;
}

/* ============================================================
   METRIC CARDS
   ============================================================ */

div[data-testid="stMetric"] {
    background-color: #0d1d31;
    border: 1px solid #214363;
    border-radius: 14px;
    padding: 16px;
}

div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] p {
    color: #aebfd1 !important;
}

div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] div {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 800 !important;
}

/* ============================================================
   BUTTONS
   ============================================================ */

.stButton button,
.stFormSubmitButton button,
.stDownloadButton button {
    background-color: #12365a !important;
    color: #ffffff !important;
    border: 1px solid #2b5a82 !important;
    border-radius: 8px;
}

.stButton button p,
.stFormSubmitButton button p,
.stDownloadButton button p {
    color: #ffffff !important;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    background-color: #1c4b76 !important;
    border-color: #4b8fca !important;
}

/* ============================================================
   TABLES
   ============================================================ */

div[data-testid="stDataFrame"],
div[data-testid="stTable"] {
    color: #ffffff !important;
}

/* Alerts and information boxes */
div[data-testid="stAlert"] p {
    color: inherit;
}

/* Disabled inputs */
input:disabled,
textarea:disabled {
    color: #cbd5e1 !important;
    -webkit-text-fill-color: #cbd5e1 !important;
    opacity: 1 !important;
}

/* Dividers */
hr {
    border-color: #203b5a;
}

/* Captions */
.stCaption,
[data-testid="stCaptionContainer"] {
    color: #b5c5d6 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. PROJECT PATHS
# app.py is in app/; CSV files are in data/
# ============================================================

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
DATA_DIR = PROJECT_DIR / "data"

# ============================================================
# 4. CLEAN COLUMN NAMES
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
# Detect comma/tab separators and tolerate malformed records
# ============================================================

def read_smart_csv(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    df = pd.read_csv(
        file_path,
        encoding="utf-8-sig",
        sep=None,
        engine="python",
        on_bad_lines="warn"
    )

    return clean_columns(df)

# ============================================================
# 6. COLLECTION ACTIONS READER
# ============================================================

def read_collection_actions_csv(file_path):
    df = read_smart_csv(file_path)

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

    # Handle older files without amount_recovered.
    if "amount_recovered" not in df.columns:
        df["amount_recovered"] = 0

    # Add missing columns with defaults.
    for column in expected_columns:
        if column not in df.columns:
            if column in ["amount_targeted", "amount_recovered"]:
                df[column] = 0
            else:
                df[column] = ""

    return df[expected_columns]

# ============================================================
# 7. LOAD ALL DATA
# ============================================================

@st.cache_data
def load_data():
    customers = read_smart_csv(DATA_DIR / "customers.csv")
    billing = read_smart_csv(DATA_DIR / "billing_records.csv")

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
    st.write("Required files inside the data folder:")

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
# 9. VALIDATE REQUIRED COLUMNS
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

for file_name, (df, expected) in required_columns.items():
    missing = [
        column for column in expected
        if column not in df.columns
    ]

    if missing:
        column_errors.append(
            f"{file_name}: missing {missing}. "
            f"Columns found: {df.columns.tolist()}"
        )

if column_errors:
    st.error("Some CSV files have unexpected column names.")

    for message in column_errors:
        st.write(message)

    st.stop()

# ============================================================
# 10. DATA TYPE CLEANING
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
    collection_actions[column] = pd.to_numeric(
        collection_actions[column],
        errors="coerce"
    ).fillna(0)

collection_actions["action_outcome"] = (
    collection_actions["action_outcome"]
    .astype(str)
    .str.strip()
    .str.title()
)

# ============================================================
# 11. DEMO LOGIN
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
        placeholder="Enter your username"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )

    if st.button("Login", use_container_width=True):
        if (
            username in USERS
            and USERS[username]["password"] == password
        ):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = USERS[username]["role"]
            st.rerun()
        else:
            st.error("Incorrect username or password.")


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

else:
    available_pages = [
        "🔎 Customer Investigation",
        "🚨 Collection & Anomaly"
    ]

# ============================================================
# 13. SIDEBAR
# ============================================================

with st.sidebar:
    st.title("⚡ Command Center")
    st.caption("DATA DETECTIVES")
    st.write(f"**User:** {current_username}")
    st.write(f"**Role:** {current_role}")
    st.divider()

    page = st.radio("Navigation", available_pages)

    if st.button("🚪 Logout", use_container_width=True):
        for key in ["logged_in", "username", "role"]:
            st.session_state.pop(key, None)
        st.rerun()

st.title("⚡ ELECTRICITY COMMAND CENTER")
st.caption("Electricity Consumption, Billing & Default Risk Analytics")
st.divider()

# ============================================================
# PAGE 1: RISK INTELLIGENCE
# ============================================================

def show_risk_intelligence():
    st.header("📊 Risk Intelligence")

    total_customers = customers["consumer_id"].nunique()
    total_consumption = billing["units_consumed"].sum()
    total_billing = billing["amount_billed"].sum()

    unpaid = billing[
        billing["payment_status"].str.lower() == "unpaid"
    ].copy()

    unpaid_customers = unpaid["consumer_id"].nunique()
    revenue_at_risk = unpaid["amount_billed"].sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Customers", f"{total_customers:,}")
    c2.metric("Total Consumption", f"{total_consumption:,.0f}")
    c3.metric("Total Billing", f"₹{total_billing:,.0f}")
    c4.metric("Unpaid Customers", f"{unpaid_customers:,}")
    c5.metric("Revenue at Risk", f"₹{revenue_at_risk:,.0f}")

    st.subheader("Dashboard Filters")
    f1, f2, f3 = st.columns(3)

    with f1:
        zones = ["All"] + sorted(
            customers["zone"].dropna().astype(str).unique().tolist()
        )
        selected_zone = st.selectbox("Zone", zones)

    with f2:
        categories = ["All"] + sorted(
            customers["category"].dropna().astype(str).unique().tolist()
        )
        selected_category = st.selectbox("Category", categories)

    with f3:
        months = ["All"] + sorted(
            billing["billing_month"].dropna()
            .dt.strftime("%Y-%m").unique().tolist()
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

    st.subheader("Monthly Electricity Consumption")
    monthly_consumption = (
        filtered_billing.groupby("billing_month")["units_consumed"]
        .sum().sort_index()
    )

    if not monthly_consumption.empty:
        st.line_chart(monthly_consumption)
    else:
        st.info("No consumption data for these filters.")

    st.subheader("Monthly Billing")
    monthly_billing = (
        filtered_billing.groupby("billing_month")["amount_billed"]
        .sum().sort_index()
    )

    if not monthly_billing.empty:
        st.line_chart(monthly_billing)
    else:
        st.info("No billing data for these filters.")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Payment Status")

        if not filtered_billing.empty:
            st.bar_chart(
                filtered_billing["payment_status"].value_counts()
            )
        else:
            st.info("No payment data.")

    with c2:
        st.subheader("Consumption Pattern")

        if "consumption_pattern" in filtered_billing.columns:
            st.bar_chart(
                filtered_billing["consumption_pattern"].value_counts()
            )
        else:
            st.info("No consumption pattern column.")

    st.subheader("Revenue at Risk by Zone")
    filtered_unpaid = filtered_billing[
        filtered_billing["payment_status"].str.lower() == "unpaid"
    ]

    if not filtered_unpaid.empty:
        zone_data = filtered_unpaid.merge(
            customers[["consumer_id", "zone"]].drop_duplicates(),
            on="consumer_id",
            how="left"
        )

        st.bar_chart(
            zone_data.groupby("zone")["amount_billed"]
            .sum().sort_values(ascending=False)
        )
    else:
        st.info("No unpaid bills for these filters.")

# ============================================================
# PAGE 2: CUSTOMER INVESTIGATION
# ============================================================

def show_customer_investigation():
    st.header("🔎 Customer Investigation")

    customer_list = sorted(
        customers["consumer_id"].dropna().astype(str).unique().tolist()
    )

    if not customer_list:
        st.warning("No customer IDs found.")
        return

    selected_customer = st.selectbox(
        "Select Consumer ID",
        customer_list
    )

    customer_data = customers[
        customers["consumer_id"].astype(str) == selected_customer
    ]

    if customer_data.empty:
        st.error("Customer not found.")
        return

    customer = customer_data.iloc[0]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Consumer ID", str(customer["consumer_id"]))
    c2.metric("Category", str(customer.get("category", "N/A")))
    c3.metric("Zone", str(customer.get("zone", "N/A")))
    c4.metric("Area", str(customer.get("area", "N/A")))
    c5.metric(
        "Sanctioned Load",
        f'{customer.get("sanctioned_load_kw", 0)} kW'
    )

    customer_billing = billing[
        billing["consumer_id"].astype(str) == selected_customer
    ].copy().sort_values("billing_month")

    st.subheader("Billing History")

    if customer_billing.empty:
        st.info("No billing records found.")

    else:
        unpaid = customer_billing[
            customer_billing["payment_status"].str.lower() == "unpaid"
        ]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            "Total Consumption",
            f'{customer_billing["units_consumed"].sum():,.0f}'
        )
        c2.metric(
            "Total Billing",
            f'₹{customer_billing["amount_billed"].sum():,.0f}'
        )
        c3.metric("Unpaid Bills", len(unpaid))
        c4.metric(
            "Revenue at Risk",
            f'₹{unpaid["amount_billed"].sum():,.0f}'
        )

        st.subheader("Monthly Consumption")
        st.line_chart(
            customer_billing.groupby("billing_month")["units_consumed"]
            .sum().sort_index()
        )

        display_columns = [
            "billing_month",
            "units_consumed",
            "amount_billed",
            "payment_status",
            "due_date",
            "payment_date"
        ]

        display_columns = [
            col for col in display_columns
            if col in customer_billing.columns
        ]

        st.dataframe(
            customer_billing[display_columns],
            use_container_width=True,
            hide_index=True
        )

    st.subheader("Customer Anomalies")

    customer_anomalies = anomalies[
        anomalies["consumer_id"].astype(str).str.strip().str.upper()
        == selected_customer.strip().upper()
    ]

    if customer_anomalies.empty:
        st.success("No anomaly records found.")
    else:
        st.dataframe(
            customer_anomalies,
            use_container_width=True,
            hide_index=True
        )

    # Record a collection action
    st.divider()
    st.subheader("Record Collection Action")

    with st.form("collection_action_form"):
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
            min_value=0.0
        )

        amount_recovered = st.number_input(
            "Amount Recovered (₹)",
            min_value=0.0
        )

        officer_id = st.text_input("Officer ID")
        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Save Action")

        if submitted:
            if not officer_id.strip():
                st.warning("Enter an Officer ID.")

            else:
                new_action = {
                    "action_id": "ACTION_" + datetime.now().strftime(
                        "%Y%m%d%H%M%S%f"
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
                    updated = pd.concat(
                        [
                            collection_actions,
                            pd.DataFrame([new_action])
                        ],
                        ignore_index=True
                    )

                    updated.to_csv(
                        DATA_DIR / "collection_actions.csv",
                        index=False
                    )

                    st.cache_data.clear()
                    st.success("Collection action saved.")
                    st.warning(
                        "Streamlit Cloud may not preserve CSV changes "
                        "after restart or redeployment."
                    )

                except Exception as error:
                    st.error(f"Could not save the action: {error}")

    st.subheader("Collection Action History")

    customer_actions = collection_actions[
        collection_actions["consumer_id"].astype(str).str.strip()
        == selected_customer.strip()
    ]

    if customer_actions.empty:
        st.info("No collection actions found.")
    else:
        st.dataframe(
            customer_actions,
            use_container_width=True,
            hide_index=True
        )

# ============================================================
# PAGE 3: COLLECTION & ANOMALY
# ============================================================

def show_collection_anomaly():
    st.header("🚨 Collection & Anomaly Intelligence")

    unpaid = billing[
        billing["payment_status"].str.lower() == "unpaid"
    ].copy()

    targeted = collection_actions["amount_targeted"].sum()
    recovered = collection_actions["amount_recovered"].sum()

    recovery_rate = (
        recovered / targeted * 100 if targeted else 0
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Unpaid Customers",
        f'{unpaid["consumer_id"].nunique():,}'
    )
    c2.metric(
        "Revenue at Risk",
        f'₹{unpaid["amount_billed"].sum():,.0f}'
    )
    c3.metric("Anomaly Cases", f"{len(anomalies):,}")
    c4.metric("Collection Actions", f"{len(collection_actions):,}")
    c5.metric(
        "Recovered Actions",
        int(
            (
                collection_actions["action_outcome"].str.lower()
                == "recovered"
            ).sum()
        )
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Amount Targeted", f"₹{targeted:,.0f}")
    c2.metric("Amount Recovered", f"₹{recovered:,.0f}")
    c3.metric("Recovery Rate", f"{recovery_rate:.2f}%")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Unpaid Customers by Zone")

        if not unpaid.empty:
            zone_data = unpaid.merge(
                customers[["consumer_id", "zone"]].drop_duplicates(),
                on="consumer_id",
                how="left"
            )

            st.bar_chart(
                zone_data.groupby("zone")["consumer_id"]
                .nunique().sort_values(ascending=False)
            )
        else:
            st.info("No unpaid bills found.")

    with c2:
        st.subheader("Collection Outcomes")
        st.bar_chart(
            collection_actions["action_outcome"].value_counts()
        )

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Anomaly Types")

        if "anomaly_type" in anomalies.columns:
            st.bar_chart(anomalies["anomaly_type"].value_counts())
        else:
            st.info("No anomaly type column.")

    with c2:
        st.subheader("Anomaly Cases by Zone")

        zone_data = anomalies.merge(
            customers[["consumer_id", "zone"]].drop_duplicates(),
            on="consumer_id",
            how="left"
        )

        st.bar_chart(
            zone_data.groupby("zone")["consumer_id"].count()
        )

    st.subheader("Recent Anomaly Records")
    st.dataframe(
        anomalies.head(100),
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# PAGE 4: RISK PREDICTION
# ============================================================

def show_risk_prediction():
    st.header("🤖 Risk Prediction & Model Performance")

    high_risk = risk_predictions[
        risk_predictions["risk_level"] == "HIGH"
    ].copy()

    low_count = (
        risk_predictions["risk_level"] == "LOW"
    ).sum()

    medium_count = (
        risk_predictions["risk_level"] == "MEDIUM"
    ).sum()

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Risk-Scored Customers",
        f'{risk_predictions["consumer_id"].nunique():,}'
    )
    c2.metric(
        "High-Risk Customers",
        f'{high_risk["consumer_id"].nunique():,}'
    )
    c3.metric(
        "Average Risk Score",
        f'{risk_predictions["risk_score"].mean():.2f}'
    )
    c4.metric("Low-Risk Records", int(low_count))
    c5.metric("Medium-Risk Records", int(medium_count))

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Risk Level Distribution")
        st.bar_chart(
            risk_predictions["risk_level"].value_counts()
        )

    with c2:
        st.subheader("High-Risk Customers by Zone")

        high_zone = high_risk.merge(
            customers[["consumer_id", "zone"]].drop_duplicates(),
            on="consumer_id",
            how="left"
        )

        st.bar_chart(
            high_zone.groupby("zone")["consumer_id"]
            .nunique().sort_values(ascending=False)
        )

    st.subheader("Average Risk Score by Zone")

    risk_zone = risk_predictions.merge(
        customers[["consumer_id", "zone"]].drop_duplicates(),
        on="consumer_id",
        how="left"
    )

    st.bar_chart(
        risk_zone.groupby("zone")["risk_score"]
        .mean().sort_values(ascending=False)
    )

    st.subheader("Risk Score Distribution")
    st.line_chart(risk_predictions[["risk_score"]])

    st.subheader("Model Information")

    c1, c2, c3 = st.columns(3)
    c1.metric("Model", "Logistic Regression")
    c2.metric("Accuracy", "71.65%")
    c3.metric("Risk Score Range", "0–100")

    st.info(
        "The table displays risk predictions loaded from your CSV file. "
        "The accuracy value is a project display value, not recalculated here."
    )

    st.subheader("Customer Risk Prioritization")

    risk_table = risk_predictions.sort_values(
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
