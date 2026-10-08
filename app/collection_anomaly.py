import streamlit as st


def show_collection_anomaly(
    customers,
    billing,
    collection_actions,
    anomalies
):

    # --------------------------------------------------
    # CLEAN COLUMN NAMES
    # --------------------------------------------------

    collection_actions.columns = (
        collection_actions.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    customers.columns = (
        customers.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    billing.columns = (
        billing.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    anomalies.columns = (
        anomalies.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # --------------------------------------------------
    # CHECK COLLECTION OUTCOME COLUMN
    # --------------------------------------------------

    if "action_outcome" not in collection_actions.columns:

        st.error(
            "The column 'action_outcome' was not found "
            "in collection_actions.csv."
        )

        st.write(
            "Available Collection Action Columns:",
            collection_actions.columns.tolist()
        )

        st.stop()

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    st.header("🚨 Collection & Anomaly Intelligence")

    st.subheader(
        "Act → Recover → Detect"
    )

    # --------------------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------------------

    unpaid_customers = billing.loc[
        billing["payment_status"] == "Unpaid",
        "consumer_id"
    ].nunique()

    revenue_at_risk = billing.loc[
        billing["payment_status"] == "Unpaid",
        "amount_billed"
    ].sum()

    anomaly_cases = len(anomalies)

    collection_actions_count = len(
        collection_actions
    )

    recovered_actions = (
        collection_actions["action_outcome"]
        .astype(str)
        .str.strip()
        .eq("Recovered")
        .sum()
    )

    # --------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Unpaid Customers",
        f"{unpaid_customers:,}"
    )

    col2.metric(
        "Revenue at Risk",
        f"₹{revenue_at_risk:,.0f}"
    )

    col3.metric(
        "Anomaly Cases",
        f"{anomaly_cases:,}"
    )

    col4.metric(
        "Collection Actions",
        f"{collection_actions_count:,}"
    )

    col5.metric(
        "Recovered Actions",
        f"{recovered_actions:,}"
    )

    # --------------------------------------------------
    # UNPAID CUSTOMERS BY ZONE
    # --------------------------------------------------

    st.subheader(
        "📍 Unpaid Customers by Zone"
    )

    unpaid_data = billing[
        billing["payment_status"] == "Unpaid"
    ]

    unpaid_by_zone = (
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
    )

    st.bar_chart(
        unpaid_by_zone
    )

    # --------------------------------------------------
    # COLLECTION OUTCOME
    # --------------------------------------------------

    st.subheader(
        "📞 Collection Outcome"
    )

    collection_outcome = (
        collection_actions[
            "action_outcome"
        ]
        .astype(str)
        .str.strip()
        .value_counts()
    )

    st.bar_chart(
        collection_outcome
    )

    # --------------------------------------------------
    # ANOMALY TYPE
    # --------------------------------------------------

    st.subheader(
        "⚠️ Anomaly Type"
    )

    anomaly_type = (
        anomalies[
            "anomaly_type"
        ]
        .astype(str)
        .str.strip()
        .value_counts()
    )

    st.bar_chart(
        anomaly_type
    )

    # --------------------------------------------------
    # ANOMALY CASES BY ZONE
    # --------------------------------------------------

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
    )

    st.bar_chart(
        anomaly_zone
    )

    # --------------------------------------------------
    # COLLECTION ACTIONS BY ZONE
    # --------------------------------------------------

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
    )

    st.bar_chart(
        actions_zone
    )

    # --------------------------------------------------
    # RECENT ANOMALY RECORDS
    # --------------------------------------------------

    st.subheader(
        "⚠️ Recent Anomaly Records"
    )

    anomaly_display = anomalies[
        [
            "consumer_id",
            "billing_month",
            "units_consumed",
            "previous_units",
            "consumption_change_pct",
            "anomaly_type",
            "amount_billed",
            "payment_status"
        ]
    ].copy()

    st.dataframe(
        anomaly_display.head(100),
        use_container_width=True,
        hide_index=True
    )
