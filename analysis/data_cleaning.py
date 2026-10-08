# ============================================================
# DATA DETECTIVES
# Data Cleaning Script
# Electricity Consumption & Bill Default Risk Prediction
# ============================================================

import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# 1. Project paths
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


# ------------------------------------------------------------
# 2. Load datasets
# ------------------------------------------------------------

customers_path = DATA_DIR / "customers.csv"
billing_path = DATA_DIR / "billing_records.csv"
collection_path = DATA_DIR / "collection_actions.csv"

customers = pd.read_csv(customers_path)
billing = pd.read_csv(billing_path)
collection = pd.read_csv(collection_path)


# ------------------------------------------------------------
# 3. Clean column names
# ------------------------------------------------------------

customers.columns = (
    customers.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

billing.columns = (
    billing.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

collection.columns = (
    collection.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)


# ------------------------------------------------------------
# 4. Clean customer data
# ------------------------------------------------------------

customers["consumer_id"] = (
    customers["consumer_id"]
    .astype(str)
    .str.strip()
)

customers["category"] = (
    customers["category"]
    .astype(str)
    .str.strip()
    .str.title()
)

customers["zone"] = (
    customers["zone"]
    .astype(str)
    .str.strip()
    .str.title()
)

customers["area"] = (
    customers["area"]
    .astype(str)
    .str.strip()
    .str.title()
)

customers["sanctioned_load_kw"] = pd.to_numeric(
    customers["sanctioned_load_kw"],
    errors="coerce"
)


# ------------------------------------------------------------
# 5. Clean billing data
# ------------------------------------------------------------

billing["consumer_id"] = (
    billing["consumer_id"]
    .astype(str)
    .str.strip()
)

billing["payment_status"] = (
    billing["payment_status"]
    .astype(str)
    .str.strip()
    .str.title()
)

billing["consumption_pattern"] = (
    billing["consumption_pattern"]
    .astype(str)
    .str.strip()
    .str.title()
)

billing["billing_month"] = pd.to_datetime(
    billing["billing_month"],
    errors="coerce"
)

billing["due_date"] = pd.to_datetime(
    billing["due_date"],
    errors="coerce"
)

billing["payment_date"] = pd.to_datetime(
    billing["payment_date"],
    errors="coerce"
)

billing["units_consumed"] = pd.to_numeric(
    billing["units_consumed"],
    errors="coerce"
)

billing["amount_billed"] = pd.to_numeric(
    billing["amount_billed"],
    errors="coerce"
)


# ------------------------------------------------------------
# 6. Clean collection actions
# ------------------------------------------------------------

collection["consumer_id"] = (
    collection["consumer_id"]
    .astype(str)
    .str.strip()
)

collection["action_type"] = (
    collection["action_type"]
    .astype(str)
    .str.strip()
    .str.title()
)

collection["action_outcome"] = (
    collection["action_outcome"]
    .astype(str)
    .str.strip()
    .str.title()
)

collection["action_date"] = pd.to_datetime(
    collection["action_date"],
    errors="coerce"
)

collection["amount_targeted"] = pd.to_numeric(
    collection["amount_targeted"],
    errors="coerce"
)

# amount_recovered was added to the project later.
# If it does not exist, create it with 0.
if "amount_recovered" not in collection.columns:
    collection["amount_recovered"] = 0

collection["amount_recovered"] = pd.to_numeric(
    collection["amount_recovered"],
    errors="coerce"
).fillna(0)


# ------------------------------------------------------------
# 7. Remove duplicate records
# ------------------------------------------------------------

customers = customers.drop_duplicates()
billing = billing.drop_duplicates()
collection = collection.drop_duplicates()


# ------------------------------------------------------------
# 8. Handle numeric missing values
# ------------------------------------------------------------

for column in ["units_consumed", "amount_billed"]:
    if column in billing.columns:
        billing[column] = billing[column].fillna(
            billing[column].median()
        )

if "sanctioned_load_kw" in customers.columns:
    customers["sanctioned_load_kw"] = customers[
        "sanctioned_load_kw"
    ].fillna(
        customers["sanctioned_load_kw"].median()
    )

if "amount_targeted" in collection.columns:
    collection["amount_targeted"] = collection[
        "amount_targeted"
    ].fillna(0)


# ------------------------------------------------------------
# 9. Validate customer IDs
# ------------------------------------------------------------

valid_customer_ids = set(customers["consumer_id"])

billing = billing[
    billing["consumer_id"].isin(valid_customer_ids)
].copy()

collection = collection[
    collection["consumer_id"].isin(valid_customer_ids)
].copy()


# ------------------------------------------------------------
# 10. Sort datasets
# ------------------------------------------------------------

billing = billing.sort_values(
    ["consumer_id", "billing_month"]
)

collection = collection.sort_values(
    ["consumer_id", "action_date"]
)


# ------------------------------------------------------------
# 11. Display cleaning summary
# ------------------------------------------------------------

print("=" * 60)
print("DATA CLEANING SUMMARY")
print("=" * 60)

print("\nCustomers:")
print("Rows:", len(customers))
print("Columns:", len(customers.columns))
print("Missing values:", customers.isna().sum().sum())
print("Duplicates:", customers.duplicated().sum())

print("\nBilling Records:")
print("Rows:", len(billing))
print("Columns:", len(billing.columns))
print("Missing values:", billing.isna().sum().sum())
print("Duplicates:", billing.duplicated().sum())

print("\nCollection Actions:")
print("Rows:", len(collection))
print("Columns:", len(collection.columns))
print("Missing values:", collection.isna().sum().sum())
print("Duplicates:", collection.duplicated().sum())


# ------------------------------------------------------------
# 12. Final validation
# ------------------------------------------------------------

print("\nPayment Status Distribution:")
print(
    billing["payment_status"]
    .value_counts(dropna=False)
)

print("\nConsumption Pattern Distribution:")
print(
    billing["consumption_pattern"]
    .value_counts(dropna=False)
)

print("\nCollection Outcome Distribution:")
print(
    collection["action_outcome"]
    .value_counts(dropna=False)
)


print("\n" + "=" * 60)
print("DATA CLEANING COMPLETED SUCCESSFULLY")
print("=" * 60)
