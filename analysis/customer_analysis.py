import pandas as pd
customers = pd.read_csv("C:/Users/Admin/Desktop/Data-Dectives/Data/customers.csv")
#Basic EDA

print(customers.head()) #see the First records
print(customers.tail()) #see last Records
print(customers.shape) #Number of rows and columns
print(customers.columns) #Column names
print(customers.info()) #Data type+missing values
print(customers.describe()) #Numerical Statistics

#Check Each Customer Category
print(customers['category'].value_counts()) #In each customer by category

#Check how many customer in each ZOne
print(customers['zone'].value_counts()) #It tells how may customers are in each group

#Checking Missing Values
print(customers.isnull().sum())

#Check Duplicate Customers
print(customers.duplicated().sum())

#Then Specfically Check duplicate IDS:
print(customers['consumer_id'].duplicated().sum()) #Becaue Every Customer has Unique ID

#Now Basic Business Questions

#1.How many customers are they
print(customers['consumer_id'].nunique())

#2.How many Domestic customers?
print("Domestic:",(customers['category']=='Domestic').sum())

#3.What is the average sanctioned load?
print(customers['sanctioned_load_kw'].mean())

#4.Which Category has the highest avaerage sanctioned load?
print(customers.groupby('category')['sanctioned_load_kw'].mean())

#5.How many customers are in each zone?
print(customers.groupby('zone')['consumer_id'].count())

#6.Find maxium sanctional load
print(customers['sanctioned_load_kw'].max())

#Find min sanctional load
print(customers['sanctioned_load_kw'].min())

#Find the average sanctional load for Domestic customers
domestic_avg = customers.loc[customers['category']=='Domestic','sanctioned_load_kw'].mean()
print(domestic_avg)

#Count customers in NOth Zone
print((customers['zone']=='North').count())

#Find number of customers in each area
print(customers.groupby('area')['consumer_id'].count())







