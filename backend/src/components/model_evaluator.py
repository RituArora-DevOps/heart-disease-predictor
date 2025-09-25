import sys
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score
from src.logger import logging
from src.exception import CustomException

def evaluate_model_performance(y_test, y_pred, y_proba, output_path):
    try:
        # Classification metrics
        conf_matrix = confusion_matrix(y_test, y_pred)
        clf_report = classification_report(y_test, y_pred, digits=4, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_proba)

        logging.info(f"Confusion Matrix:\n{conf_matrix}")
        logging.info(f"Classification Report:\n{clf_report}")

        # Save metrics to a text file
        with open(output_path, 'w') as f:
            f.write("Confusion Matrix (threshold=0.5):\n")
            f.write(f"{conf_matrix}\n\n")
            f.write("Classification Report (threshold=0.5):\n")
            f.write(clf_report)
            f.write(f"ROC AUC Score: {roc_auc: .4f}\n")
        
        logging.info(f"Model performance metrics saved to {output_path}")
        return roc_auc
    
    except Exception as e:
        raise CustomException(e, sys)