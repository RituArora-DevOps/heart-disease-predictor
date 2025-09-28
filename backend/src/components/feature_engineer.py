import os
import sys
import pandas as pd
import numpy as np
# from src.exception import CustomException
# from src.logger import logging

# NOTE: Adjust paths if your project structure is different
# Your data_ingestion.py reads from 'notebook\data\cleaned_data.csv'
RAW_DATA_PATH = 'notebook/data/cleaned_data.csv'
ENGINEERED_DATA_PATH = 'notebook/data/engineered_data.csv'

class FeatureEngineer:
    """
    Component for creating new, potentially more powerful features from existing ones 
    to address low importance of numerical features (like BMI and Exercise).
    """
    def __init__(self):
        os.makedirs(os.path.dirname(ENGINEERED_DATA_PATH), exist_ok=True)

    def initiate_feature_engineering(self, input_path=RAW_DATA_PATH, output_path=ENGINEERED_DATA_PATH):
        try:
            print(f"Starting Feature Engineering from {input_path}...")
            
            # 1. Load Data
            df = pd.read_csv(input_path)

            # 2. Derive Standard BMI (The most critical new feature)
            # Formula: weight (kg) / (height (m))^2
            df['BMI_calculated'] = df['Weight_(kg)'] / (df['Height_(cm)'] / 100)**2
            print(f"-> Created new feature 'BMI_calculated'.")

            # 3. Handle the Exercise feature's near-zero importance
            # We will keep the original 'Exercise' column in the dataset, but rely on 
            # its ordinal encoding in the preprocessor. No new derived feature is strictly necessary here yet,
            # as the fix is primarily about testing the raw BMI feature.

            # 4. Save the new DataFrame
            df.to_csv(output_path, index=False, header=True)
            print(f"Feature Engineering completed. New data saved to {output_path}")

            return output_path

        except Exception as e:
            # Raise your CustomException here
            print(f"An error occurred during feature engineering: {e}", file=sys.stderr)

if __name__ == '__main__':
    engineer = FeatureEngineer()
    engineer.initiate_feature_engineering()