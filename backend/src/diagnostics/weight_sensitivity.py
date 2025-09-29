import numpy as np
import pandas as pd
import joblib  # or use your own load_object if you have it
from math import log

# Load model and preprocessor
model = joblib.load('artifacts/model.pkl') 
preprocessor = joblib.load('artifacts/preprocessor.pkl')

# Base input (from your shared row)
base_input = {
    'General_Health': 'Good',
    'Checkup': 'Within the past year',
    'Exercise': 'Yes',
    'Skin_Cancer': 'No',
    'Other_Cancer': 'No',
    'Depression': 'No',
    'Diabetes': 'No',
    'Arthritis': 'No',
    'Sex': 'Female',
    'Age_Category': '55-59',
    'Height_(cm)': 160,  # Fixed height
    'Smoking_History': 'Yes',
    'Alcohol_Consumption': 0,
    'Fruit_Consumption': 30,
    'Green_Vegetables_Consumption': 4,
    'FriedPotato_Consumption': 2
}

# Vary weight and generate predictions
weights = [60, 80, 100, 120, 150, 200, 250, 270]

print("Weight Sensitivity Test:")
print("=" * 60)
for w in weights:
    row = base_input.copy()
    row['Weight_(kg)'] = w

    # Calculate derived columns
    bmi = w / ((row['Height_(cm)'] / 100) ** 2)
    row['BMI'] = round(bmi, 2)

    row['Weight_(kg)_log'] = log(w + 1)
    row['BMI_log'] = log(bmi + 1)
    row['Alcohol_Consumption_log'] = log(row['Alcohol_Consumption'] + 1)
    row['Fruit_Consumption_log'] = log(row['Fruit_Consumption'] + 1)
    row['Green_Vegetables_Consumption_log'] = log(row['Green_Vegetables_Consumption'] + 1)
    row['FriedPotato_Consumption_log'] = log(row['FriedPotato_Consumption'] + 1)

    # Convert to DataFrame
    df = pd.DataFrame([row])

    # Preprocess and predict
    X_processed = preprocessor.transform(df)
    prob = model.predict_proba(X_processed)[0][1]  # Probability of class 1 (Heart Disease)

    print(f"Weight: {w:>3} kg | BMI: {bmi:5.2f} | Risk probability: {prob:.4f}")
