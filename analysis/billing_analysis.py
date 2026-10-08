import pandas as pd
customers = pd.read_csv('C:/Users/Admin/Desktop/Data-Dectives/Data/customers.csv')
billing = pd.read_csv('C:/Users/Admin/Desktop/Data-Dectives/Data/billing_records.csv')

print(billing.head())
print(billing.head()) #see the First records
print(billing.tail()) #see last Records
print(billing.shape) #Number of rows and columns #it shows 10,000 customers * 12 months = 1,20,000 records(1,20,000,8)
print(billing.columns) #Column names
print(billing.info()) #Data type+missing values
print(billing.describe()) #Numerical Statistics

print(billing.isnull().sum()) #it shows in payment_date is 1734 that means unpaid

#convert Date columns
billing['billing_month'] = pd.to_datetime(
    billing['billing_month']
)

billing['due_date'] = pd.to_datetime(
    billing['due_date'])

billing['payment_date'] = pd.to_datetime(
    billing['payment_date'])


print(billing.dtypes)

#Check Duplicate records
print(billing.duplicated().sum())

#Consumption Analysis
#Toal consumaption
print(billing['units_consumed'].sum())

#Average consumption
print(billing['units_consumed'].mean())

#Max consumption
print(billing['units_consumed'].max())

#min consumption
print(billing['units_consumed'].min())

#Bill Analysis
#Total Bill amount
print(billing['amount_billed'].sum())

#Average Bill
print(billing['amount_billed'].mean())

#Highest bill
print(billing['amount_billed'].max())

#lowest Bill
print(billing['amount_billed'].min())

#Payment Status Analysis
print(billing['payment_status'].value_counts())

#Then Percentage
print(billing['payment_status'].value_counts(normalize = True).mul(100).round(2))

#Find Unpaid Bills
unpaid = billing[
    billing['payment_status'] == 'Unpaid'
    ]
print(unpaid.head())
print(unpaid.shape)

#Find Consumpation Anomalies
print(billing['consumption_pattern'].value_counts())

anomailes = billing[
    billing['consumption_pattern'].isin(['Spike','Drop'])]
print(anomailes.head())

#Monthly Analysis
monthly_consumption = billing.groupby('billing_month')['units_consumed'].sum()
print(monthly_consumption)

#Average monthly bill
monthly_bill = billing.groupby('billing_month')['amount_billed'].mean()
print(monthly_bill)

#Business Questions
#Which month has the highest electricty concumption
print(billing.groupby('billing_month')['units_consumed'].max())
#TO get only highest month
highest_month = monthly_consumption.idxmax()
print("Highest_month:",highest_month)



#which month has the highest total billing
monthly_billing =billing.groupby('billing_month')['amount_billed'].sum()
highest_billing_month = monthly_billing.idxmax()
highest_billing = monthly_billing.max()
print("Highest_billing_month:",highest_billing_month)
print("Total billing:",highest_billing)


#3.What percentage of bills are unpaid
unpaid_percentage = (
    (billing['payment_status'] == 'Unpaid').mean() * 100 )
print("unpaid percentage:",round(unpaid_percentage,2),'%')

#4,Which customers have frequent late paymeants?
late_payments = billing[billing['payment_status']=='Late'].groupby("consumer_id").size()
print(late_payments.sort_values(ascending = False).head(10))



#5.First Monthly Summary using agg
monthly_summary = billing.groupby("billing_month").agg(
    total_consumption=("units_consumed", "sum"),
    average_consumption=("units_consumed", "mean"),
    total_billing=("amount_billed", "sum"),
    average_bill=("amount_billed", "mean"),
    number_of_bills=("consumer_id", "count")
)

print(monthly_summary)


#Adavnaced Analysis

#Highest Billing
highest_billing = monthly_summary.sort_values(
    "total_billing",
    ascending=False
)

print(highest_billing)

#Top 5 consumption months
top_5_consumption = monthly_summary.sort_values(
    "total_consumption",
    ascending=False
).head(5)

print(top_5_consumption)

#Filtering:Unpaid bills above ₹20,000

high_unpaid_bills = billing[
    (billing["payment_status"] == "Unpaid") &
    (billing["amount_billed"] > 20000)
]

print(high_unpaid_bills.head())

#Unpaid + high consumption:Multiple conditions
high_risk_bills = billing[
    (billing["payment_status"] == "Unpaid") &
    (billing["units_consumed"] > 500)
]

print(high_risk_bills.head())

#Calculated Column — Bill per Unit
billing["bill_per_unit"] = (
    billing["amount_billed"] /
    billing["units_consumed"]
)

print(
    billing[
        [
            "consumer_id",
            "units_consumed",
            "amount_billed",
            "bill_per_unit"
        ]
    ].head()
)


#Payment Delay
billing["payment_delay_days"] = (
    billing["payment_date"] -
    billing["due_date"]
).dt.days

print(
    billing[
        ["consumer_id", "due_date",
         "payment_date", "payment_delay_days"]
    ].head()
)

#Merge
billing_customer = billing.merge(
    customers,
    on="consumer_id",
    how="left"
)

print(billing_customer.head())
print(billing_customer.columns)

#Customer-Level Analysis
#Total consumption per customer
customer_consumption = billing.groupby(
    "consumer_id"
)["units_consumed"].sum()

print(
    customer_consumption
    .sort_values(ascending=False)
    .head(10)
)
#Total billing per customer
customer_billing = billing.groupby(
    "consumer_id"
)["amount_billed"].sum()

print(
    customer_billing
    .sort_values(ascending=False)
    .head(10)
)
#Number of unpaid bills per customer
customer_unpaid = billing[
    billing["payment_status"] == "Unpaid"
].groupby("consumer_id").size()

print(
    customer_unpaid
    .sort_values(ascending=False)
    .head(10)
)

#Zone Analysis


zone_consumption = billing_customer.groupby(
    "zone"
)["units_consumed"].sum()

print(
    zone_consumption
    .sort_values(ascending=False)
)

#This tells us which zone has the highest total electricity consumption.

#Category Analysis
category_consumption = billing_customer.groupby(
    "category"
)["units_consumed"].sum()

print(
    category_consumption
    .sort_values(ascending=False)
)



zone_payment = billing_customer.groupby(
    ["zone", "payment_status"]
).size()

print(zone_payment)

#This lets us see how many Paid, Late, and Unpaid bills exist in each zone.

#Consumption Anomaly Analysis

abnormal = billing[
    billing["consumption_pattern"].isin(
        ["Spike", "Drop"]
    )
]

print(abnormal.head())
print("Abnormal records:", len(abnormal))
#Customers with the most abnormal records
abnormal_customers = abnormal.groupby(
    "consumer_id"
).size().sort_values(
    ascending=False
)


print(abnormal_customers.head(10))




unpaid = billing[
    billing["payment_status"] == "Unpaid"
]

revenue_at_risk = unpaid["amount_billed"].sum()

print(
    "Revenue at Risk: ₹",
    round(revenue_at_risk, 2)
)

print(
    "Number of Unpaid Bills:",
    len(unpaid)
)



















