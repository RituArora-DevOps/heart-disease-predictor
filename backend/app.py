from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
import os
import uvicorn
import dill
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database.database_config import get_db_session, create_db_tables
from services.api_service import log_assessment

# Initialize app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",             
        "http://127.0.0.1:5173",
        "https://our-frontend-domain.com"
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATABASE STARTUP EVENT ---
@app.on_event("startup")
def on_startup():
    """Create database tables on startup if they don't exist."""
    create_db_tables()
    print("Database tables ensured/created.")

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

# This list must match the exact 25 columns and order expected by the preprocessor
FINAL_COLUMNS = [
    'General_Health', 'Checkup', 'Exercise', 'Skin_Cancer', 'Other_Cancer', 
    'Depression', 'Diabetes', 'Arthritis', 'Sex', 'Age_Category', 
    'Height_(cm)', 'Weight_(kg)', 'Smoking_History', 
    'Alcohol_Consumption', 'Fruit_Consumption', 'Green_Vegetables_Consumption', 
    'FriedPotato_Consumption',
    # Engineered Features (Must be passed through):
    'Weight_(kg)_log', 'BMI_log', 'BMI_calculated', 
    'BMI_Age_Interaction', 'Exercise_Health_Interaction',
    # Capped Log Features (CRITICAL FIX)
    'Alcohol_Consumption_log_capped', 'Fruit_Consumption_log_capped', 
    'Green_Vegetables_Consumption_log_capped', 'FriedPotato_Consumption_log_capped' 
]

# Inference route
@app.post('/predict', response_model=PredictionResponse)
def predict(data: PatientData, db: Session = Depends(get_db_session)):
    try:
        input_dict = data.model_dump()
        
        # 1. Compute BMI
        input_dict["BMI"] = input_dict["Weight_kg"] / ((input_dict["Height_cm"]/100) ** 2)
        
        # --- FEATURE ENGINEERING (Replicate data_transformation.py logic) ---
        
        # 2. Compute log features (using log1p)
        input_dict["Weight_(kg)_log"] = np.log1p(input_dict["Weight_kg"])
        input_dict["BMI_log"] = np.log1p(input_dict["BMI"])
        input_dict["Alcohol_Consumption_log"] = np.log1p(input_dict["Alcohol_Consumption"])
        input_dict["Fruit_Consumption_log"] = np.log1p(input_dict["Fruit_Consumption"])
        input_dict["Green_Vegetables_Consumption_log"] = np.log1p(input_dict["Green_Vegetables_Consumption"])
        input_dict["FriedPotato_Consumption_log"] = np.log1p(input_dict["FriedPotato_Consumption"])

        # 3. Apply Capping to Consumption Logs (CRITICAL FIX)
        CAP_VALUE = 4.0 # Assuming cap from training
        input_dict["Alcohol_Consumption_log_capped"] = np.clip(input_dict["Alcohol_Consumption_log"], a_min=None, a_max=CAP_VALUE)
        input_dict["Fruit_Consumption_log_capped"] = np.clip(input_dict["Fruit_Consumption_log"], a_min=None, a_max=CAP_VALUE)
        input_dict["Green_Vegetables_Consumption_log_capped"] = np.clip(input_dict["Green_Vegetables_Consumption_log"], a_min=None, a_max=CAP_VALUE)
        input_dict["FriedPotato_Consumption_log_capped"] = np.clip(input_dict["FriedPotato_Consumption_log"], a_min=None, a_max=CAP_VALUE)

        # 4. Compute BMI_calculated 
        input_dict["BMI_calculated"] = input_dict["BMI"]

        # 5. Compute Interaction Features (Using VERIFIED Ordinal Mappings)
        
        # VERIFIED: 18-24=0, 80+=12 (Risk increases with score)
        age_map = {'18-24': 0, '25-29': 1, '30-34': 2, '35-39': 3, '40-44': 4, '45-49': 5, 
           '50-54': 6, '55-59': 7, '60-64': 8, '65-69': 9, '70-74': 10, '75-79': 11, '80+': 12}
           
        # VERIFIED: Poor=0, Excellent=4 (Risk decreases as score increases)
        health_map = {'Poor': 0, 'Fair': 1, 'Good': 2, 'Very Good': 3, 'Excellent': 4} 
        
        # CORRECTED FOR RISK: No=1 (Risk), Yes=0 (Protection). Makes interaction higher for 'No'.
        exercise_map = {'Yes': 0, 'No': 1}
        
        age_score = age_map.get(input_dict["Age_Category"], 0)
        health_score = health_map.get(input_dict["General_Health"], 0)
        exercise_score = exercise_map.get(input_dict["Exercise"], 0)
        
        input_dict["BMI_Age_Interaction"] = input_dict["BMI_log"] * age_score
        input_dict["Exercise_Health_Interaction"] = exercise_score * health_score
        
        # 6. Rename/Adjust keys to match preprocessor expectations (original names)
        input_dict["Height_(cm)"] = input_dict.pop("Height_cm")
        input_dict["Weight_(kg)"] = input_dict.pop("Weight_kg")
        
        # 7. Create DataFrame from all features
        df = pd.DataFrame([input_dict])
        
        # 8. Select and order the columns the preprocessor expects
        df_for_transform = df[FINAL_COLUMNS]

        # Transform
        transformed_data = preprocessor.transform(df_for_transform)

        # Predict probability
        probability = model.predict_proba(transformed_data)[0][1]
        
        # Use the global optimal threshold
        prediction = int(probability >= OPTIMAL_THRESHOLD)

        # CRITICAL AUDIT STEP: Call the imported, robust logging function
        log_assessment(db, input_dict, probability, bool(prediction))

        return PredictionResponse(
            prediction=prediction,
            probability=round(probability, 4), 
            threshold_used=round(OPTIMAL_THRESHOLD, 4)
        )

    # Specific error handling: If log_assessment raised HTTPException (our 500 error), re-raise it
    except HTTPException:
        raise
        
    # Catch all other prediction or data transformation errors
    except Exception as e:
        # Log the error for debugging
        print(f"Prediction failed due to model/data error: {e}")
        # Return a generic 500 to the user to hide internal details
        raise HTTPException(
            status_code=500, 
            detail="Prediction failed due to an internal server error. Please check your input."
        )

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)