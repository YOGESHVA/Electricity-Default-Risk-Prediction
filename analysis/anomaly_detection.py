import pandas as pd

# ============================================================
# 1. LOAD BILLING DATA
# ============================================================

billing = pd.read_csv("../data/billing_records.csv")

print("Billing data loaded successfully!")
print("Shape:", billing.shape)
print()


# ============================================================
# 2. CONVERT BILLING MONTH TO DATE
# ============================================================

billing["billing_month"] = pd.to_datetime(
    billing["billing_month"]
)

# Sort customer-wise and month-wise
billing = billing.sort_values(
    ["consumer_id", "billing_month"]
)


# ============================================================
# 3. CALCULATE PREVIOUS MONTH CONSUMPTION
# ============================================================

billing["previous_units"] = (
    billing
    .groupby("consumer_id")["units_consumed"]
    .shift(1)
)


# ============================================================
# 4. CALCULATE MONTH-TO-MONTH CHANGE %
# ============================================================

billing["consumption_change_pct"] = (
    (
        billing["units_consumed"]
        - billing["previous_units"]
    )
    / billing["previous_units"]
) * 100


# ============================================================
# 5. IDENTIFY ANOMALIES
# ============================================================

def identify_anomaly(change):

    if pd.isna(change):
        return "Normal"

    elif change >= 70:
        return "Spike"

    elif change <= -70:
        return "Drop"

    else:
        return "Normal"


billing["anomaly_type"] = (
    billing["consumption_change_pct"]
    .apply(identify_anomaly)
)


# ============================================================
# 6. CREATE ANOMALY FLAG
# ============================================================

billing["is_anomaly"] = (
    billing["anomaly_type"] != "Normal"
).astype(int)


# ============================================================
# 7. CREATE ANOMALY DATASET
# ============================================================

anomalies = billing[
    billing["is_anomaly"] == 1
].copy()


# ============================================================
# 8. SELECT IMPORTANT COLUMNS
# ============================================================

anomaly_output = anomalies[
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


# ============================================================
# 9. SAVE ANOMALY RESULTS
# ============================================================

anomaly_output.to_csv(
    "../data/anomaly_detection_results.csv",
    index=False
)


# ============================================================
# 10. DISPLAY RESULTS
# ============================================================

print("Anomaly detection completed!")
print()

print("Total billing records:", len(billing))
print("Total anomaly cases:", len(anomaly_output))
print()

print("Anomaly distribution:")
print(
    anomaly_output["anomaly_type"]
    .value_counts()
)

print()

print("Sample anomaly records:")
print(
    anomaly_output.head(10)
)

print()

print(
    "File saved successfully:"
)

print(
    "../data/anomaly_detection_results.csv"
)
# ============================================================
# 11. VERIFY ANOMALY RESULTS
# ============================================================

print("Anomaly file verification:")
print()

print("Total anomaly records:", len(anomaly_output))

print()

print("Spike cases:")
print(
    (anomaly_output["anomaly_type"] == "Spike").sum()
)

print()

print("Drop cases:")
print(
    (anomaly_output["anomaly_type"] == "Drop").sum()
)

print()

print("Highest consumption changes:")
print(
    anomaly_output[
        [
            "consumer_id",
            "billing_month",
            "consumption_change_pct",
            "anomaly_type"
        ]
    ]
    .sort_values(
        "consumption_change_pct",
        ascending=False
    )
    .head(10)
)
