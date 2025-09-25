import sys
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score, precision_recall_curve, f1_score
import matplotlib.pyplot as plt
from src.logger import logging
from src.exception import CustomException

def tune_threshold(y_test, y_proba, curve_path, report_path, num_thresholds=100):
    try:
        logging.info("Generating Precision-Recall vs Threshold curve...")

        # Calculate precision, recall, and thresholds
        precision, recall, thresholds = precision_recall_curve(y_test, y_proba)
        # f1_scores = 2 * (precision * recall) / (precision + recall + 1e-6)  # Avoid division by zero

        # Plot Precision-Recall vs Threshold curve
        plt.figure(figsize=(10, 6))
        plt.plot(thresholds, precision[:-1], label='Precision', color='b')
        plt.plot(thresholds, recall[:-1], label='Recall', color='g')
        # plt.plot(thresholds, f1_scores[:-1], label='F1 Score', color='r')
        plt.xlabel('Threshold')
        plt.ylabel('Precision / Recall')
        plt.title('Precision-Recall vs Threshold')
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.savefig(curve_path)
        plt.close()
        logging.info(f"Precision-Recall vs Threshold curve saved to {curve_path}")

        # Reduce number of thresholds
        threshold_to_test = np.linspace(0, 1, num_thresholds)
        best_f1=0
        best_threshold=0.5
        best_metrics={}

        for t in threshold_to_test:
            y_pred = (y_proba >= t).astype(int)
            if y_pred.sum()==0:
                continue
            f1=f1_score(y_test, y_pred, zero_division=0)            
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = t
                cm = confusion_matrix(y_test, y_pred)
                cr = classification_report(y_test, y_pred, digits=4, zero_division=0)
                best_metrics = {
                    'F1 Score': best_f1,
                    'Threshold': best_threshold,
                    'Confusion Matrix': cm,
                    'Classification Report': cr
                }
        with open(report_path, 'w') as f:
            f.write(f"Optimal Threshold: {best_threshold:.4f}\n")
            f.write(f"F1 Score at Optimal Threshold: {best_f1:.4f}\n")
            f.write("Confusion Matrix at Optimal Threshold:\n")
            f.write(np.array2string(best_metrics['Confusion Matrix']))
            f.write("Classification Report at Optimal Threshold:\n")
            f.write(best_metrics['Classification Report'])

        logging.info(f"Threshold tuning completed. Optimal threshold: {best_threshold:.4f}, F1 Score: {best_f1:.4f}")
        logging.info(f"Threshold report saved to {report_path}")
        return best_threshold, best_f1, best_metrics

    except Exception as e:
        raise CustomException(e, sys)