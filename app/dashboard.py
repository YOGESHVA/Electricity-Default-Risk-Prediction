import streamlit as st


def show_dashboard(customers, billing):

    st.header("📊 Electricity Risk Intelligence")

    # KPI calculations
    total_customers = customers["consumer_id"].nunique()

    total_consumption = billing["units_consumed"].sum()

    total_billing = billing["amount_billed"].sum()

    unpaid_customers = billing.loc[
        billing["payment_status"] == "Unpaid",
        "consumer_id"
    ].nunique()

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Customers",
        f"{total_customers:,}"
    )

    col2.metric(
        "Total Consumption",
        f"{total_consumption:,.0f}"
    )

    col3.metric(
        "Total Billing",
        f"₹{total_billing:,.0f}"
    )

    col4.metric(
        "Unpaid Customers",
        f"{unpaid_customers:,}"
    )

    # Monthly consumption
    st.subheader(
        "📈 Monthly Electricity Consumption"
    )

    monthly_consumption = (
        billing
        .groupby("billing_month")["units_consumed"]
        .sum()
    )

    st.line_chart(monthly_consumption)

    # Payment status
    st.subheader("💳 Payment Status")

    payment_status = (
        billing["payment_status"]
        .value_counts()
    )

    st.bar_chart(payment_status)

    # Revenue at risk
    st.subheader("💰 Revenue at Risk")

    revenue_at_risk = billing.loc[
        billing["payment_status"] == "Unpaid",
        "amount_billed"
    ].sum()

    st.metric(
        "Unpaid Billing Amount",
        f"₹{revenue_at_risk:,.0f}"
    )

import streamlit as st


def show_dashboard(customers, billing):

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    st.header(
        "📊 Electricity Risk Intelligence"
    )


    # --------------------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------------------

    total_customers = customers[
        "consumer_id"
    ].nunique()


    total_consumption = billing[
        "units_consumed"
    ].sum()


    total_billing = billing[
        "amount_billed"
    ].sum()


    unpaid_customers = billing.loc[
        billing["payment_status"] == "Unpaid",
        "consumer_id"
    ].nunique()


    # --------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "Total Customers",
        f"{total_customers:,}"
    )


    col2.metric(
        "Total Consumption",
        f"{total_consumption:,.0f}"
    )


    col3.metric(
        "Total Billing",
        f"₹{total_billing:,.0f}"
    )


    col4.metric(
        "Unpaid Customers",
        f"{unpaid_customers:,}"
    )


    # --------------------------------------------------
    # MONTHLY CONSUMPTION
    # --------------------------------------------------

    st.subheader(
        "📈 Monthly Electricity Consumption"
    )


    monthly_consumption = (
        billing
        .groupby("billing_month")[
            "units_consumed"
        ]
        .sum()
    )


    st.line_chart(
        monthly_consumption
    )


    # --------------------------------------------------
    # PAYMENT STATUS
    # --------------------------------------------------

    st.subheader(
        "💳 Payment Status"
    )


    payment_status = (
        billing[
            "payment_status"
        ].value_counts()
    )


    st.bar_chart(
        payment_status
    )


    # --------------------------------------------------
    # REVENUE AT RISK
    # --------------------------------------------------

    st.subheader(
        "💰 Revenue at Risk"
    )


    revenue_at_risk = billing.loc[
        billing["payment_status"] == "Unpaid",
        "amount_billed"
    ].sum()


    st.metric(
        "Unpaid Billing Amount",
        f"₹{revenue_at_risk:,.0f}"
    )
