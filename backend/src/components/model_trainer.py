import os
import sys
import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from catboost import CatBoostClassifier

from sklearn.metrics import (
    roc_auc_score,
    confusion_matrix,
    classification_report,
    precision_recall_curve,
    f1_score
)

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object, evaluate_models

@dataclass
class ModelTrainerConfig:
    trained_model_file_path=os.path.join('artifacts', 'model.pkl')
    metrics_file_path = os.path.join('artifacts', 'model_metrics.txt')
    threshold_cuve_path = os.path.join('artifacts', 'precision_recall_threshold_curve.png')
    threshold_metrics_path = os.path.join('artifacts', 'model_threshold_metrics.txt')

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config=ModelTrainerConfig()

    def initiate_model_trainer(self, train_array, test_array):
        try:
            logging.info('Splitting training and testing arrays into X and y...')
            X_train, y_train, X_test, y_test = (
                train_array[:, :-1],
                train_array[:, -1],
                test_array[:, :-1],
                test_array[:, -1]
            )

            models = {
                "Logistic Regression": LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
                "Random Forest": RandomForestClassifier(class_weight='balanced', random_state=42),
                "Decision Tree": DecisionTreeClassifier(random_state=42),
                "Gradient Boosting": GradientBoostingClassifier(random_state=42),
                "K-Neighbors": KNeighborsClassifier(),
                "XGBClassifier": XGBClassifier(eval_metric='logloss', random_state=42),
                "CatBoosting Classifier": CatBoostClassifier(verbose=False, random_seed=42),
                "AdaBoost Classifier": AdaBoostClassifier(random_state=42),
            }

            params = {
                "Logistic Regression": {
                    'C': [0.01, 0.1, 1, 10],
                    'solver': ['lbfgs', 'liblinear']
                },
                "Random Forest": {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [None, 10, 20]
                },
                "Decision Tree": {
                    'criterion': ['gini', 'entropy'],
                    'max_depth': [None, 10, 20]
                },
                "Gradient Boosting": {
                    'learning_rate': [0.01, 0.1],
                    'n_estimators': [50, 100],
                    'subsample': [0.8, 1.0]
                },
                "K-Neighbors": {
                    'n_neighbors': [3, 5, 7]
                },
                "XGBClassifier": {
                    'learning_rate': [0.01, 0.1],
                    'n_estimators': [50, 100]
                },
                "CatBoosting Classifier": {
                    'depth': [6, 8, 10],
                    'learning_rate': [0.01, 0.1],
                    'iterations': [50, 100]
                },
                "AdaBoost Classifier": {
                    'learning_rate': [0.01, 0.1, 0.5],
                    'n_estimators': [50, 100]
                }
            }

            logging.info('Starting model evaluation using cross-validation (ROC AUC)...')
            model_report, best_models, predictions = evaluate_models(X_train, y_train, X_test, y_test, models, params, metric='roc_auc')

            best_model_name = max(model_report, key=model_report.get)
            best_model = best_models[best_model_name]
            best_model_score = model_report[best_model_name]
            y_pred = predictions[best_model_name]['y_pred']
            y_pred_proba = predictions[best_model_name]['y_proba']

            logging.info(f"Best model found: {best_model_name} with ROC AUC score: {best_model_score: .4f}")

            if best_model_score < 0.6:
                raise CustomException("No model found with ROC AUC score above the threshold of 0.6", sys)
            
            logging.info('Saving the best model to disk...')
            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )

            # Classification metrics
            conf_matrix = confusion_matrix(y_test, y_pred)
            clf_report = classification_report(y_test, y_pred, digits=4, zero_division=0)
            roc_auc = roc_auc_score(y_test, y_pred_proba)

            logging.info(f"Confusion Matrix:\n{conf_matrix}")
            logging.info(f"Classification Report:\n{clf_report}")

            # Save metrics to a text file
            with open(self.model_trainer_config.metrics_file_path, 'w') as f:
                f.write(f"Best Model: {best_model_name}\n")
                f.write(f"ROC AUC Score: {best_model_score: .4f}\n\n")
                f.write("Confusion Matrix (threshold=0.5):\n")
                f.write(f"{conf_matrix}\n\n")
                f.write("Classification Report (threshold=0.5):\n")
                f.write(clf_report)
            
            # Threshold tuning plot
            precision, recall, thresholds = precision_recall_curve(y_test, y_pred_proba)
            plt.figure(figsize=(8, 6))
            plt.plot(thresholds, precision[:-1], 'b--', label='Precision', linewidth=2)
            plt.plot(thresholds, recall[:-1], 'g-', label='Recall', linewidth=2)
            plt.xlabel('Threshold')
            plt.ylabel('Precision/Recall')
            plt.title('Precision and Recall vs Threshold')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(self.model_trainer_config.threshold_cuve_path)
            plt.close()
            logging.info(f'Precision-Recall vs Threshold curve saved to {self.model_trainer_config.threshold_cuve_path}')

            # Find optimal threshold based on F1 Score
            best_f1 = 0
            best_threshold=0.5
            best_metrics = {}

            for t in thresholds:
                y_pred_threshold = (y_pred_proba >= t).astype(int)

                 # Skip thresholds where no positive predictions are made
                if y_pred_threshold.sum() == 0:
                    continue

                current_f1 = f1_score(y_test, y_pred_threshold, zero_division=0)

                if current_f1 > best_f1:
                    best_f1 = current_f1
                    best_threshold = t
                    cm = confusion_matrix(y_test, y_pred_threshold)
                    cr = classification_report(y_test, y_pred_threshold, digits=4, output_dict=False, zero_division=0)
                    best_metrics = {
                        'confusion_matrix': cm,
                        'classification_report': cr,
                        'f1_score': best_f1,
                        'threshold': best_threshold
                    }
            
            logging.info(f'Best threshold found: {best_threshold: .4f} with F1 Score: {best_f1: .4f}')

            # Save threshold-tuned metrics to a text file
            with open(self.model_trainer_config.threshold_metrics_path, 'w') as f:
                f.write(f"Best Threshold: {best_threshold: .4f}\n")
                f.write(f"F1 Score at Best Threshold: {best_f1: .4f}\n\n")
                f.write("Confusion Matrix at Best Threshold:\n")
                f.write(np.array2string(best_metrics['confusion_matrix']))
                f.write("Classification Report at Best Threshold:\n")
                f.write(best_metrics['classification_report'])

            logging.info(f"Best threshold found: {best_threshold: .4f} with F1 Score: {best_f1: .4f}")

            return roc_auc

        except Exception as e:
            raise CustomException(e, sys)