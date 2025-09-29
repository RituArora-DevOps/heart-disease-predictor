import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.inspection import permutation_importance
from src.utils import load_object
from src.exception import CustomException
from src.logger import logging

# Set artifact paths
MODEL_PATH = os.path.join('artifacts', 'model.pkl')
PREPROCESSOR_PATH = os.path.join('artifacts', 'preprocessor.pkl')
TEST_ARRAY_PATH = os.path.join('artifacts', 'test_array.npy')
FEATURE_IMPORTANCE_PLOT_PATH = os.path.join('artifacts', 'feature_importance.png')
FEATURE_IMPORTANCE_CSV_PATH = os.path.join('artifacts', 'feature_importance.csv')

def get_feature_names(preprocessor):
    """
    Extract feature names after preprocessing (for column transformer).
    """
    try:
        # Get names from the numerical pipeline (StandardScaler has get_feature_names_out)
        num_features = list(preprocessor.named_transformers_['num']['scaler'].get_feature_names_out())

        # Get names used by the binary pipeline (these are the original column names)
        # Note: BinaryEncoder in DataTransformation creates one column per input binary feature.
        binary_features_input = preprocessor.transformers_[1][2] # Get the list of column names fed into 'bin'
        
        # Get names used by the ordinal pipeline (these are the original column names)
        ordinal_features_input = preprocessor.transformers_[2][2] # Get the list of column names fed into 'ord'
 
        # The output order is: [Num cols] + [Binary cols] + [Ordinal cols]
        feature_names = num_features + binary_features_input + ordinal_features_input
        return np.array(feature_names) # Return as numpy array to match expected type
    except Exception as e:
        raise CustomException("Failed to extract feature names from preprocessor", sys)

def analyze_feature_importance():
    try:
        logging.info("Starting feature importance analysis using permutation importance...")

        # Load artifacts
        logging.info("Loading model, preprocessor, and test data...")
        model = load_object(MODEL_PATH)
        preprocessor = load_object(PREPROCESSOR_PATH)
        test_array = np.load(TEST_ARRAY_PATH)

        X_test = test_array[:, :-1]
        y_test = test_array[:, -1]

        # Get feature names
        logging.info("Extracting feature names from preprocessor...")
        feature_names = get_feature_names(preprocessor)

        logging.info("Running permutation importance...")
        result = permutation_importance(
            model, X_test, y_test,
            n_repeats=10,
            random_state=42,
            scoring='roc_auc',
            n_jobs=-1
        )

        importances = result.importances_mean
        std = result.importances_std

        # Create DataFrame for easy viewing and export
        importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': importances,
            'Std': std
        }).sort_values(by='Importance', ascending=False)

        logging.info("Saving feature importance data and plot...")

        # Save as CSV
        importance_df.to_csv(FEATURE_IMPORTANCE_CSV_PATH, index=False)

        # Plot
        top_n = 20
        top_features = importance_df.head(top_n)
        plt.figure(figsize=(12, 8))
        plt.barh(top_features['Feature'][::-1], top_features['Importance'][::-1], xerr=top_features['Std'][::-1])
        plt.xlabel("Mean Decrease in ROC AUC")
        plt.title(f"Top {top_n} Important Features (Permutation Importance)")
        plt.tight_layout()
        plt.savefig(FEATURE_IMPORTANCE_PLOT_PATH)
        plt.close()

        logging.info(f"Feature importance plot saved to {FEATURE_IMPORTANCE_PLOT_PATH}")
        logging.info(f"Feature importance CSV saved to {FEATURE_IMPORTANCE_CSV_PATH}")

        print("\nTop 10 Features by Importance:")
        print(importance_df.head(10))

    except Exception as e:
        raise CustomException(e, sys)

if __name__ == "__main__":
    analyze_feature_importance()
