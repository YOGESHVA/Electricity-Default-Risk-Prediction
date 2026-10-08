import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,classification_report,confusion_matrix

#Load ML Dataset
data = pd.read_csv("../data/ml_default_risk_dataset.csv")
print("Dataset Loaded succeddfully!")
print("Shape:",data.shape)

#Select Features
features = [
    "total_bills",
    "total_units",
    "average_units",
    "average_bill",
    "total_bill_amount",
    "unpaid_count",
    "late_count",
    "unpaid_percentage",
]
x = data[features]
y = data["default"]

#Split data into training and testing
X_train,X_test,y_train,y_test = train_test_split(
    x,
    y,
    test_size = 0.20,
    random_state = 42,
    stratify = y
)
print("Training Rows:",len(X_train))
print("Testing rows:",len(X_test))

#Creat Logistic Regression model
model = LogisticRegression(
    max_iter = 1000
)

#Train the model
model.fit(X_train,y_train)
print("Model training completed")

#Make predictions
y_pred = model.predict(X_test)

#Calculate accurarcy
accuracy = accuracy_score(y_test,y_pred)

print("\nModel Accuracy:",accuracy)

#Classification report
print("\nClassification Report:")
print(classification_report(y_test,y_pred))

#Confusion matrix
print("\nConfusion Matrix:")
print(confusion_matrix(y_test,y_pred))

#

import joblib
joblib.dump(model,"../models/default_risk_model.pkl")
print("Model saved successfully!")


