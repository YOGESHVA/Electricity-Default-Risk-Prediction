import pandas as pd
import matplotlib.pyplot as plt

#Monthly Electricty Consumption Trend

billing = pd.read_csv("C:/Users/Admin/Desktop/Data-Dectives/Data/billing_records.csv")
print(billing.head(5))
print(billing.columns)

customers = pd.read_csv("C:/Users/Admin/Desktop/Data-Dectives/Data/customers.csv")
print(customers.head())


"""billing['billing_month'] = pd.to_datetime( #we have date and time
    billing['billing_month']
)
print(billing)


monthly_consumption = billing.groupby('billing_month')['units_consumed'].sum()

plt.figure(figsize=(10,5))

plt.plot(
    monthly_consumption.index,
    monthly_consumption.values,
    marker = 'o'
    )
plt.title('Monthly Electricity Concumption')
plt.xlabel('Month')
plt.ylabel('Total Units Concumes')
plt.xticks(rotation = 45)
plt.tight_layout()
plt.show()

#Monthly Billing Trend

monthly_billing = billing.groupby(
    'billing_month')['amount_billed'].sum()

plt.figure(figsize = (10,5))
plt.plot(
    monthly_billing.index,
    monthly_billing.values,
    marker = 'o'
)
plt.title('Monthly Total Biling')
plt.xlabel('Month')
plt.ylabel('Total Biling Amount')
plt.xticks(rotation = 45)
plt.tight_layout()
plt.show() #simple Flow:Billing Records-Group by Month-sum(amount_billed)-monthly billing trend-line chart


#Payment Status Distribution
payment_status_counts = billing['payment_status'].value_counts()
print(payment_status_counts)

plt.figure(figsize=(8,5))


plt.bar(
    payment_status_counts.index,
    payment_status_counts.values
)
plt.title("Payment Status Distribution")
plt.xlabel("Payment Status")
plt.ylabel("Number of Bills")
plt.tight_layout()
plt.show() #Flow:Billing_data - payment_status - value countss() - paid/late/unpaid - Bar chart

#Consumpation Pattern Anlysis
#Normal vs Spike vs Drop

consumption_pattern_counts = billing['consumption_pattern'].value_counts()
print(consumption_pattern_counts)

plt.figure(figsize=(8,5))

plt.bar(
    consumption_pattern_counts.index,
    consumption_pattern_counts.values
)
plt.title('Electricty Concumpation Pattern')
plt.xlabel('Consumation Pattern')
plt.ylabel("Number of Bills")

plt.tight_layout()
plt.show() #Flow:Billing[consumaption_pattern]-value_counts()-Normal/spike/Drop-Bar chart"""


#Category Analysis
#Now we compare electricty consumption between Domestic,Commerical,Industrial

billing_customer = billing.merge(
    customers,
    on='consumer_id',
    how = 'left'
)
category_consumption = billing_customer.groupby(
    'category')['units_consumed'].sum()
print(category_consumption)

plt.figure(figsize=(8,5))
plt.bar(category_consumption.index,
        category_consumption.values
)
plt.title('Electricty Consumaption by Customer Category')
plt.xlabel('Customer Category')
plt.ylabel('Total Units Consumed')

plt.tight_layout()
plt.show() #logic:billing - customers - merge - category - groupby(category) - sum(units_consume) - Bar chart



#Electricity Consumption by Zone
zone_consumption = billing_customer.groupby(
    "zone"
)["units_consumed"].sum()

print(zone_consumption)

plt.figure(figsize=(8, 5))

plt.bar(
    zone_consumption.index,
    zone_consumption.values
)

plt.title("Electricity Consumption by Zone")
plt.xlabel("Zone")
plt.ylabel("Total Units Consumed")

plt.tight_layout()
plt.show()

#Unpaid Bills Analysis
unpaid = billing[
    billing["payment_status"] == "Unpaid"
]

unpaid_by_month = unpaid.groupby(
    "billing_month"
)["amount_billed"].sum()

print(unpaid_by_month)

plt.figure(figsize=(10, 5))

plt.bar(
    unpaid_by_month.index,
    unpaid_by_month.values
)

plt.title("Unpaid Billing Amount by Month")
plt.xlabel("Billing Month")
plt.ylabel("Unpaid Amount")

plt.xticks(rotation=45)
plt.tight_layout()

plt.show()

#Customer-Level Analysis

#Now we move from month-level analysis to customer-level analysis.

#Our goal is to identify customers who have:

#High total electricity consumption
#High total billing
#Many unpaid bills
#1. Total consumption by customer
customer_consumption = billing.groupby(
    "consumer_id"
)["units_consumed"].sum()

print(
    customer_consumption
    .sort_values(ascending=False)
    .head(10)
)

#This gives the Top 10 customers by electricity consumption.

#2. Total billing by customer
customer_billing = billing.groupby(
    "consumer_id"
)["amount_billed"].sum()

print(
    customer_billing
    .sort_values(ascending=False)
    .head(10)
)

#This gives the Top 10 customers by total billing amount.

#3. Customers with the most unpaid bills
customer_unpaid = billing[
    billing["payment_status"] == "Unpaid"
].groupby(
    "consumer_id"
).size()

print(
    customer_unpaid
    .sort_values(ascending=False)
    .head(10)
)


#Unpaid Bills by Zone

unpaid_zone = billing_customer[
    billing_customer["payment_status"] == "Unpaid"
].groupby(
    "zone"
).size()

print(unpaid_zone)

plt.figure(figsize=(8, 5))

plt.bar(
    unpaid_zone.index,
    unpaid_zone.values
)

plt.title("Unpaid Bills by Zone")
plt.xlabel("Zone")
plt.ylabel("Number of Unpaid Bills")

plt.tight_layout()
plt.show()

# Anomaly Visualization 🔎

#Now we focus only on abnormal electricity consumption.



#Find customers who have the highest number of abnormal consumption records.

#1. Filter abnormal records
abnormal = billing[
    billing["consumption_pattern"].isin(
        ["Spike", "Drop"]
    )
]

print(abnormal.head())

print(
    "Total Abnormal Records:",
    len(abnormal)
)
#2. Count anomalies by customer
abnormal_customers = abnormal.groupby(
    "consumer_id"
).size().sort_values(
    ascending=False
)

print(
    abnormal_customers.head(10)
)
#3. Create Top 10 chart
top_10_anomalies = abnormal_customers.head(10)

plt.figure(figsize=(10, 5))

plt.bar(
    top_10_anomalies.index.astype(str),
    top_10_anomalies.values
)

plt.title("Top 10 Customers with Abnormal Consumption")
plt.xlabel("Consumer ID")
plt.ylabel("Number of Abnormal Records")

plt.xticks(rotation=45)
plt.tight_layout()

plt.show()


#Final EDA Analysis: Revenue at Risk
#How much money is currently at risk because of unpaid bills

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


#Revenue at Risk by Zone
#Which zones have the highest unpaid billing amount?

#1. Calculate unpaid amount by zone
unpaid_zone_amount = billing_customer[
    billing_customer["payment_status"] == "Unpaid"
].groupby(
    "zone"
)["amount_billed"].sum()

print(unpaid_zone_amount)

#2. Create the chart
plt.figure(figsize=(8, 5))

plt.bar(
    unpaid_zone_amount.index,
    unpaid_zone_amount.values
)

plt.title("Revenue at Risk by Zone")
plt.xlabel("Zone")
plt.ylabel("Unpaid Billing Amount")

plt.tight_layout()
plt.show()










