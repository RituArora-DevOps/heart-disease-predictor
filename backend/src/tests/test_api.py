import requests
import pytest
import pandas as pd

# The API endpoint URL
API_URL = "http://127.0.0.1:8000/predict"
OPTIMAL_THRESHOLD = 0.1919

# --- Fixture to check API connectivity (optional but good practice) ---
@pytest.fixture(scope="session", autouse=True)
def check_api_connection():
    """Checks if the FastAPI server is running before running tests."""
    try:
        requests.get(API_URL.replace("/predict", "/"), timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail("FastAPI server is not running at http://127.0.0.1:8000. Please start the server first.")


# --- Test Data Parameters ---
# Use pytest.mark.parametrize to run a single test function with multiple data sets.
# Format: (test_name, data_profile, expected_prediction, min_prob, max_prob)
TEST_CASES = [
    # 1. Low Risk Profile (P < 0.05)
    ("Low Risk", {
        "General_Health": "Excellent", "Checkup": "Within the past year", "Exercise": "Yes", 
        "Skin_Cancer": "No", "Other_Cancer": "No", "Depression": "No", "Diabetes": "No", 
        "Arthritis": "No", "Sex": "Female", "Age_Category": "18-24", "Height_cm": 170.0, 
        "Weight_kg": 60.0, "Smoking_History": "No", "Alcohol_Consumption": 0.0, 
        "Fruit_Consumption": 30.0, "Green_Vegetables_Consumption": 30.0, "FriedPotato_Consumption": 0.0
    }, 0, None, 0.08),

    # 2. High Risk Profile (P > 0.35)
    ("High Risk", {
        "General_Health": "Poor", "Checkup": "5 or more years ago", "Exercise": "No", 
        "Skin_Cancer": "Yes", "Other_Cancer": "Yes", "Depression": "Yes", "Diabetes": "Yes", 
        "Arthritis": "Yes", "Sex": "Male", "Age_Category": "80+", "Height_cm": 175.0, 
        "Weight_kg": 100.0, "Smoking_History": "Yes", "Alcohol_Consumption": 30.0, 
        "Fruit_Consumption": 0.0, "Green_Vegetables_Consumption": 0.0, "FriedPotato_Consumption": 30.0
    }, 1, 0.30, None),

    # 3. Threshold-Crossing Profile (P > 0.1919, but < 0.30)
    # This is the profile that resulted in P = 25.32%
    ("Threshold Crossing", {
        "General_Health": "Fair", "Checkup": "Within the past year", "Exercise": "No", 
        "Skin_Cancer": "No", "Other_Cancer": "No", "Depression": "No", "Diabetes": "Yes", 
        "Arthritis": "No", "Sex": "Male", "Age_Category": "80+", "Height_cm": 175.0, 
        "Weight_kg": 100.0, "Smoking_History": "Yes", "Alcohol_Consumption": 0.0, 
        "Fruit_Consumption": 0.0, "Green_Vegetables_Consumption": 0.0, "FriedPotato_Consumption": 0.0
    }, 1, OPTIMAL_THRESHOLD, 0.30)
]


# --- Test Function using Parameterize ---
@pytest.mark.parametrize("name, data, expected_prediction, min_prob, max_prob", TEST_CASES)
def test_api_prediction(name, data, expected_prediction, min_prob, max_prob):
    """Tests the prediction endpoint against defined profiles."""
    try:
        response = requests.post(API_URL, json=data)
        response.raise_for_status() 
        result = response.json()
        
        probability = result.get('probability')
        prediction = result.get('prediction')

    except requests.exceptions.RequestException as e:
        # Fail the test if connection or HTTP error occurs
        pytest.fail(f"API Request Failed: {e}")
        
    # Assertion 1: Check the prediction class (0 or 1)
    # Pytest automatically shows a detailed comparison if this fails.
    assert prediction == expected_prediction, \
        f"Prediction Mismatch for {name}: Expected {expected_prediction}, but got {prediction} (P={probability:.4f})."

    # Assertion 2: Check the probability range for validation purposes
    if min_prob is not None:
        assert probability >= min_prob, \
            f"Probability too low for {name}: {probability:.4f} < Min Expected {min_prob:.4f}."
            
    if max_prob is not None:
        assert probability <= max_prob, \
            f"Probability too high for {name}: {probability:.4f} > Max Expected {max_prob:.4f}."

    print(f"PASS: {name} | P={probability:.4f} | Prediction={prediction}")