# In src/diagnostics/shap_analyzer.py

import os
import sys
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt

# Assuming you have load_object in src/utils.py
from src.utils import load_object

# --- Configuration ---
MODEL_PATH = 'artifacts/model.pkl'
PREPROCESSOR_PATH = 'artifacts/preprocessor.pkl' # Needed only for feature names
TEST_ARRAY_PATH = 'artifacts/test_array.npy' # Preprocessed X_test and y_test array

# --- Feature Name Extraction (Still needed for labels) ---

def get_feature_names(preprocessor):
    """
    Extract feature names after preprocessing using the saved preprocessor object.
    """
    try:
        # Get names from the numerical pipeline (StandardScaler has get_feature_names_out)
        # Assuming the structure: num (0) -> scaler
        num_features = list(preprocessor.named_transformers_['num']['scaler'].get_feature_names_out())
        
        # Get names used by the binary pipeline 
        binary_features_input = preprocessor.transformers_[1][2]
        
        # Get names used by the ordinal pipeline
        ordinal_features_input = preprocessor.transformers_[2][2]
        
        # NOTE: This assumes the ColumnTransformer output order is: num -> binary -> ordinal
        feature_names = num_features + binary_features_input + ordinal_features_input
        return np.array(feature_names)
    except Exception as e:
        print(f"Failed to extract feature names from preprocessor: {e}")
        return None

# --- SHAP Analysis Function ---

def analyze_shap_values():
    try:
        # 1. Load Artifacts and Data
        model = load_object(file_path=MODEL_PATH)
        preprocessor = load_object(file_path=PREPROCESSOR_PATH)
        
        # Load the fully processed numerical test array
        full_test_array = np.load(TEST_ARRAY_PATH)
        
        # Separate features (X) from the target (y)
        X_test_processed = full_test_array[:, :-1]
        
        # Get feature names for the SHAP plots
        feature_names = get_feature_names(preprocessor)
        if feature_names is None:
            raise Exception("Could not retrieve feature names.")

        # Convert processed data back to a DataFrame for labeling (SHAP uses this for axis labels)
        # CRITICAL: Force to float64 to prevent ufunc errors
        X_test_df = pd.DataFrame(X_test_processed, columns=feature_names).astype(np.float64)
        
        # --- 2. Calculate SHAP Values ---
        explainer = shap.TreeExplainer(model)
        
        # Use a large, representative subset (sampling the already processed data)
        X_sample = X_test_df.sample(n=10000, random_state=42)
        
        # Calculate SHAP values
        shap_values = explainer.shap_values(X_sample)
        
        print("\n--- SHAP Analysis Completed. Generating Plots ---")

        # --- 3. Prepare SHAP Matrix for Plotting (Dimension and Type Fix) ---
        
        # Convert output to a NumPy array for safe shape checking
        shap_values_array = np.array(shap_values, dtype=object) 

        # Determine the correct 2D matrix (samples x features)
        if shap_values_array.ndim == 3:
            # Binary classification list: select index 1 (the positive class)
            shap_matrix_for_plots = shap_values_array[1] 
        else:
            # Regression/Log-odds output: use the single matrix directly
            shap_matrix_for_plots = shap_values_array 
            
        # CRITICAL: Ensure the SHAP values are also standard float64
        shap_matrix_for_plots = np.array(shap_matrix_for_plots, dtype=np.float64)

        print(f"SHAP Matrix shape used for plotting: {shap_matrix_for_plots.shape}")

        # --- 4. Generate Visualizations ---

        # A. SHAP Bar Plot (Global Feature Importance: Mean Absolute SHAP)
        plt.figure(figsize=(10, 8))
        shap.summary_plot(shap_matrix_for_plots, X_sample, plot_type="bar", show=False)
        plt.title("SHAP Bar Plot: Average Magnitude of Impact on Positive Class")
        plt.tight_layout()
        plt.savefig("reports/shap_bar_plot.png")
        plt.close()

        # B. SHAP Summary Plot (Magnitude and Direction - Bee Swarm)
        plt.figure(figsize=(10, 12))
        shap.summary_plot(shap_matrix_for_plots, X_sample, show=False) 
        plt.title("SHAP Summary Plot: Impact Direction and Magnitude on Positive Class")
        plt.tight_layout()
        plt.savefig("reports/shap_summary_plot.png")
        plt.close()
        print("-> Saved SHAP Summary Plot and Bar Plot to reports/.")

        # C. SHAP Dependence Plot (Analyzing the BMI_Age_Interaction)
        plt.figure(figsize=(8, 6))
        shap.dependence_plot(
            "BMI_Age_Interaction", 
            shap_matrix_for_plots, 
            X_sample, 
            interaction_index="Age_Category", 
            show=False
        )
        plt.title("SHAP Dependence Plot: BMI_Age_Interaction vs. Age_Category")
        plt.tight_layout()
        plt.savefig("reports/shap_dependence_plot_bmi_age.png")
        plt.close()
        print("-> Saved SHAP Dependence Plot for BMI-Age Interaction to reports/.")
        
        print("\nSHAP analysis complete. Review the generated images in the 'reports' folder.")

    except Exception as e:
        print(f"An error occurred during SHAP analysis: {e}", file=sys.stderr)
        # Optionally re-raise the exception: raise CustomException(e, sys)

if __name__ == '__main__':
    # Ensure the reports directory exists
    os.makedirs('reports', exist_ok=True) 
    analyze_shap_values()