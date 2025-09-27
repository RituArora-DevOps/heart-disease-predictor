from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
import os
import uvicorn
import dill
from fastapi.middleware.cors import CORSMiddleware

# Initialize app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",             
        "http://127.0.0.1:5173",
        "https://our-frontend-domain.com"
    ], # Replace with frontend domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ARTIFACT LOADING CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, 'artifacts')

PREPROCESSOR_PATH = os.path.join(ARTIFACTS_DIR, 'preprocessor.pkl')
MODEL_PATH = os.path.join(ARTIFACTS_DIR, 'model.pkl')
OPTIMAL_THRESHOLD_PATH = os.path.join(ARTIFACTS_DIR, 'optimal_threshold.txt')

# Load pre-trained artifacts
try:
    model = dill.load(open(MODEL_PATH, 'rb'))
    preprocessor = dill.load(open(PREPROCESSOR_PATH, 'rb'))
    
    # Load the optimal threshold calculated during the evaluation step
    with open(OPTIMAL_THRESHOLD_PATH, 'r') as f:
        OPTIMAL_THRESHOLD = float(f.read())
    
    print(f"Artifacts loaded successfully. Optimal Threshold: {OPTIMAL_THRESHOLD:.4f}")
    
except FileNotFoundError as e:
    # If artifacts aren't found, raise a startup error
    print(f"Error loading required artifact: {e}")
    raise Exception("Model artifacts not found. Please run the full MLOps pipeline first.")

# Define input schema
class PatientData(BaseModel):
    General_Health: str
    Checkup: str
    Exercise: str
    Skin_Cancer: str
    Other_Cancer: str
    Depression: str
    Diabetes: str
    Arthritis: str
    Sex: str
    Age_Category: str
    Height_cm: float
    Weight_kg: float
    Smoking_History: str
    Alcohol_Consumption: float
    Fruit_Consumption: float
    Green_Vegetables_Consumption: float
    FriedPotato_Consumption: float

# Output response schema
class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    threshold_used: float

# The required order of features (original and engineered) that MUST be passed to the preprocessor.
# This list is based on the column definitions in data_transformation.py.
FINAL_COLUMNS_FOR_PREPROCESSOR = [
    'Height_(cm)', 'Weight_(kg)_log', 'BMI_log', 'Alcohol_Consumption_log', 
    'Fruit_Consumption_log', 'Green_Vegetables_Consumption_log', 
    'FriedPotato_Consumption_log', 
    'Exercise', 'Skin_Cancer', 'Other_Cancer', 'Depression', 'Arthritis', 
    'Smoking_History',
    'General_Health', 'Checkup', 'Age_Category', 'Sex', 'Diabetes'
]


# Inference route
@app.post('/predict', response_model=PredictionResponse)
def predict(data: PatientData):
    try:
        # Covert input to dict
        input_dict = data.model_dump()

        # --- Feature Engineering (Must match data_transformation.py) ---
        
        # 1. Compute BMI
        input_dict["BMI"] = input_dict["Weight_kg"] / ((input_dict["Height_cm"]/100) ** 2)

        # 2. Compute log features (using log1p as in training)
        input_dict["Weight_(kg)_log"] = np.log1p(input_dict["Weight_kg"])
        input_dict["BMI_log"] = np.log1p(input_dict["BMI"])
        input_dict["Alcohol_Consumption_log"] = np.log1p(input_dict["Alcohol_Consumption"])
        input_dict["Fruit_Consumption_log"] = np.log1p(input_dict["Fruit_Consumption"])
        input_dict["Green_Vegetables_Consumption_log"] = np.log1p(input_dict["Green_Vegetables_Consumption"])
        input_dict["FriedPotato_Consumption_log"] = np.log1p(input_dict["FriedPotato_Consumption"])

        # 3. Rename keys to match preprocessor expectations (original physical metrics)
        input_dict["Height_(cm)"] = input_dict.pop("Height_cm")
        input_dict["Weight_(kg)"] = input_dict.pop("Weight_kg")
        
        # 4. Create DataFrame from all generated features
        df = pd.DataFrame([input_dict])
        
        # 5. Select and order only the 18 columns the preprocessor expects
        df_for_transform = df[FINAL_COLUMNS_FOR_PREPROCESSOR]

        # Transform
        transformed_data = preprocessor.transform(df_for_transform)

        # Predict probability
        probability = model.predict_proba(transformed_data)[0][1]
        
        # Use the global optimal threshold
        prediction = int(probability >= OPTIMAL_THRESHOLD)

        return PredictionResponse(
            prediction=prediction,
            probability=round(probability, 4), 
            threshold_used=round(OPTIMAL_THRESHOLD, 4)
        )

    except Exception as e:
        # Log the error for debugging
        print(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed due to an internal error: {e}")

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
