import sys
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score
from src.logger import logging
from src.exception import CustomException

def evaluate_model_performance(y_test, y_pred, y_proba, output_path):
    """
    Calculates standard model performance metrics (Confusion Matrix, 
    Classification Report, ROC AUC) using the default threshold (0.5).
    Saves the report to the specified output_path.
    
    Args:
        y_test (array): True labels.
        y_pred (array): Predicted labels (at 0.5 threshold).
        y_proba (array): Predicted probabilities.
        output_path (str): File path to save the metrics report.

    Returns:
        float: The calculated ROC AUC score.
    """
    try:
        # Calculate standard classification metrics
        conf_matrix = confusion_matrix(y_test, y_pred)
        # Use zero_division=0 to prevent warnings/errors when a class is not predicted
        clf_report = classification_report(y_test, y_pred, digits=4, zero_division=0)
        
        # ROC AUC score uses the predicted probabilities
        roc_auc = roc_auc_score(y_test, y_proba)

        logging.info(f"Confusion Matrix (Default 0.5):\n{conf_matrix}")
        logging.info(f"Classification Report (Default 0.5):\n{clf_report}")
        logging.info(f"ROC AUC Score: {roc_auc: .4f}")

        # Save metrics to a text file
        with open(output_path, 'w') as f:
            f.write("--- Model Performance Metrics (Threshold = 0.5) ---\n\n")
            f.write("Confusion Matrix:\n")
            f.write(f"{conf_matrix}\n\n")
            f.write("Classification Report:\n")
            f.write(clf_report)
            f.write(f"ROC AUC Score: {roc_auc: .4f}\n")
        
        logging.info(f"Model performance metrics saved to {output_path}")
        return roc_auc
    
    except Exception as e:
        raise CustomException(e, sys)
