import pandas as pd
billing = pd.read_csv("C:/Users/Admin/Desktop/Data-Dectives/Data/billing_records.csv")
print(billing.head())

#Convert date column
billing['billing_month'] = pd.to_datetime(billing['billing_month'])

#Split historical data and future tagret period
history = billing[
    billing['billing_month']<='2025-09-01'].copy()

future = billing[billing['billing_month']>='2025-10-01'].copy()


#Create customer_level features from historical data
ml_features = history.groupby('consumer_id').agg(
    total_bills = ('consumer_id','count'),
    total_units = ('units_consumed','sum'),
    average_units = ('units_consumed','mean'),
    average_bill = ('amount_billed','mean'),
    total_bill_amount = ('amount_billed','sum')
    ).reset_index()

#count unpaid bills
unpaid = (
    history.assign(
        unpaid_flag = (history['payment_status']== "unpaid").astype(int)).groupby('consumer_id')['unpaid_flag'].sum()
    .reset_index(name = "unpaid_count"))

#Count late bills
late = (
    history.assign(
        late_flag = (history['payment_status'] == "Late").astype(int))
    .groupby("consumer_id")["late_flag"].sum()
    .reset_index(name = "late_count"))

#Merge Features
ml_features = ml_features.merge(
    unpaid,
    on = 'consumer_id',
    how = 'left'
)

ml_features = ml_features.merge(
    late,
    on = 'consumer_id',
    how = 'left'
)

#Calculate percentages
ml_features ['unpaid_percentage'] =(
    ml_features['unpaid_count']/ ml_features['total_bills'])*100

ml_features ['unpaid_percentage'] =(
    ml_features['late_count']/ ml_features['total_bills'])*100

#Create future default target
# 9. Create future default target

future["default_flag"] = (
    future["payment_status"]
    .astype(str)
    .str.strip()
    .eq("Unpaid")
    .astype(int)
)

future_default = (
    future.groupby("consumer_id")["default_flag"]
    .max()
    .reset_index(name="default")
)
#Add target to Ml dataset
ml_dataset = ml_features.merge(
    future_default,
    on = 'consumer_id',
    how = 'left'
)

#Customers without future records are treated as non-default
ml_dataset['default'] = ml_dataset['default'].fillna(0).astype(int)

#Save ML Dataset
ml_dataset.to_csv(
    "../data/ml_default_risk_dataset.csv",
    index = False
)

#Check default distribution
ml_dataset = pd.read_csv("../data/ml_default_risk_dataset.csv")
print(ml_dataset['default'].value_counts())

#
future_check = billing[
    billing['billing_month']>='2025-10-01']
print("\nOctober-December payment status:")
print(future_check['payment_status'].value_counts())


#Display results
print("Ml Dataset created successfully!")
print()
print("Shpae:",ml_dataset.shape)
print()
print("Coulmns:")
print(ml_dataset.columns.tolist())
print()
print("Default distribution:")
print(ml_dataset['default'].value_counts())
print()
print("First 5 rows:")
print(ml_dataset.head())






