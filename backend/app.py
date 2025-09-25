from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
import os
import uvicorn
import joblib
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

# Load pre-trained artifacts (preprocessor and models)
BASE_DIR = os.path.dirname(__file__)
PREPROCESSOR_PATH = os.path.join(BASE_DIR,'artifacts', 'preprocessor.pkl')
MODEL_PATH = os.path.join(BASE_DIR,'artifacts','model.pkl')

model=joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)

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
    BMI: float
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

# Final DataFrame (match training format exactly)
columns_order = [
    "General_Health", "Checkup", "Exercise", "Skin_Cancer", "Other_Cancer", "Depression",
    "Diabetes", "Arthritis", "Sex", "Age_Category",
    "Height_(cm)", "Weight_(kg)", "BMI", "Smoking_History",
    "Alcohol_Consumption", "Fruit_Consumption", "Green_Vegetables_Consumption", "FriedPotato_Consumption",
    "Weight_(kg)_log", "BMI_log", "Alcohol_Consumption_log", "Fruit_Consumption_log",
    "Green_Vegetables_Consumption_log", "FriedPotato_Consumption_log"
]

# Inference route
@app.post('/predict', response_model=PredictionResponse)
def predict(data: PatientData):
    try:
        # Covert input to dict
        input_dict = data.model_dump()

        # Compute log features
        input_dict["Weight_(kg)_log"] = np.log1p(input_dict["Weight_kg"])
        input_dict["BMI_log"] = np.log1p(input_dict["BMI"])
        input_dict["Alcohol_Consumption_log"] = np.log1p(input_dict["Alcohol_Consumption"])
        input_dict["Fruit_Consumption_log"] = np.log1p(input_dict["Fruit_Consumption"])
        input_dict["Green_Vegetables_Consumption_log"] = np.log1p(input_dict["Green_Vegetables_Consumption"])
        input_dict["FriedPotato_Consumption_log"] = np.log1p(input_dict["FriedPotato_Consumption"])

        # Rename keys to match what model expects
        input_dict["Height_(cm)"] = input_dict.pop("Height_cm")
        input_dict["Weight_(kg)"] = input_dict.pop("Weight_kg")

        df = pd.DataFrame([input_dict])[columns_order]

        # Transform
        transformed_data = preprocessor.transform(df)

        # Predict probability
        probability = model.predict_proba(transformed_data)[0][1]
        threshold = 0.5
        prediction = int(probability >= threshold)

        return PredictionResponse(
            prediction=prediction,
            probability=round(probability, 4), 
            threshold_used=threshold
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)