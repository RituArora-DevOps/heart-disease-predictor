# In src/components/feature_engineer.py

import os
import sys
import pandas as pd
import numpy as np
# from src.exception import CustomException
# from src.logger import logging

# --- Configuration ---
RAW_DATA_PATH = 'notebook/data/cleaned_data.csv'
ENGINEERED_DATA_PATH = 'notebook/data/engineered_data_v2.csv' # V2 to show this is the second iteration

# --- Define the necessary Ordinal Mappings for Feature Engineering ---
# These Mappings are necessary ONLY to create the INTERACTION FEATURES.
AGE_MAPPING = {
    '18-24': 1, '25-29': 2, '30-34': 3, '35-39': 4, '40-44': 5,
    '45-49': 6, '50-54': 7, '55-59': 8, '60-64': 9, '65-69': 10,
    '70-74': 11, '75-79': 12, '80+': 13
}

HEALTH_MAPPING = {
    'Poor': 1, 'Fair': 2, 'Good': 3, 'Very Good': 4, 'Excellent': 5
}

class FeatureEngineer:
    def __init__(self):
        os.makedirs(os.path.dirname(ENGINEERED_DATA_PATH), exist_ok=True)

    def initiate_feature_engineering(self, input_path=RAW_DATA_PATH, output_path=ENGINEERED_DATA_PATH):
        try:
            print(f"Starting V2 Feature Engineering from {input_path}...")
            
            df = pd.read_csv(input_path)

            # 1. Recalculate Standard BMI (Kept from V1)
            df['BMI_calculated'] = df['Weight_(kg)'] / (df['Height_(cm)'] / 100)**2
            print(f"-> Recalculated 'BMI_calculated'.")

            # --- STEP A: Create TEMPORARY numerical variables for interaction calculation ---
            # These are immediately dropped after the interaction features are calculated.
            df['Age_Numeric_Temp'] = df['Age_Category'].map(AGE_MAPPING)
            df['General_Health_Numeric_Temp'] = df['General_Health'].map(HEALTH_MAPPING)

            # 2. FEATURE INTERACTION 1: BMI * Age (Numerical * Ordinal)
            df['BMI_Age_Interaction'] = df['BMI_calculated'] * df['Age_Numeric_Temp'] 
            print(f"-> Created interaction feature 'BMI_Age_Interaction'.")

            # 3. FEATURE INTERACTION 2: Exercise * General Health (Binary * Ordinal)
            exercise_factor = df['Exercise'].map({'Yes': 1, 'No': 0})
            df['Exercise_Health_Interaction'] = exercise_factor * df['General_Health_Numeric_Temp']
            print(f"-> Created interaction feature 'Exercise_Health_Interaction'.")
            
            # --- STEP B: Drop the TEMPORARY numerical columns ONLY. ---
            df.drop(columns=['Age_Numeric_Temp', 'General_Health_Numeric_Temp'], inplace=True)
            print("-> Dropped temporary numerical mapping columns to avoid pipeline conflict.")


            # 4. Simple Outlier Capping (Winsorizing on consumption logs)
            consumption_cols = [
                'Alcohol_Consumption_log', 'Fruit_Consumption_log',
                'Green_Vegetables_Consumption_log', 'FriedPotato_Consumption_log'
            ]
            for col in consumption_cols:
                cap = df[col].quantile(0.99)
                df[f'{col}_capped'] = np.where(df[col] > cap, cap, df[col])
            print(f"-> Capped extreme outliers in consumption features.")

            # Drop the original log columns to avoid redundancy with the new capped log columns
            df.drop(columns=consumption_cols, inplace=True)
            
            # 5. Save the new DataFrame
            df.to_csv(output_path, index=False, header=True)
            print(f"V2 Feature Engineering completed. New data saved to {output_path}")

            return output_path

        except Exception as e:
            # raise CustomException(e, sys)
            print(f"An error occurred during feature engineering: {e}", file=sys.stderr)


if __name__ == '__main__':
    engineer = FeatureEngineer()
    engineer.initiate_feature_engineering()