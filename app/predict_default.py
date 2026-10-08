import joblib
import pandas as pd

# Load trained model
model = joblib.load("../models/default_risk_model.pkl")

print("Model loaded successfully!")

# Example customer data
customer = pd.DataFrame({
    "total_bills": [9],
    "total_units": [4000],
    "average_units": [444.44],
    "average_bill": [3000],
    "total_bill_amount": [27000],
    "unpaid_count": [2],
    "late_count": [3],
    "unpaid_percentage": [22.22]
})

# Predict default
prediction = model.predict(customer)

print("Prediction:", prediction[0])

if prediction[0] == 1:
    print("Risk Level: HIGH")
else:
    print("Risk Level: LOW")


# Predict default
prediction = model.predict(customer)

# Get default probability
probability = model.predict_proba(customer)[0][1]

# Convert probability to risk score
risk_score = probability * 100

print("Prediction:", prediction[0])
print("Risk Score:", round(risk_score, 2))

if risk_score >= 70:
    print("Risk Level: HIGH")
elif risk_score >= 40:
    print("Risk Level: MEDIUM")
else:
    print("Risk Level: LOW")

