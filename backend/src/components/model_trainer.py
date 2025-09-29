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

# Note: Removed imports for model_evaluator and threshold_tuner

@dataclass
class ModelTrainerConfig:
    trained_model_file_path=os.path.join('artifacts', 'model.pkl')
    # New path to save the test array for later evaluation
    test_array_path = os.path.join('artifacts', 'test_array.npy')
    # Evaluation artifact paths are now defined in the dedicated evaluator pipeline
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
                "XGBClassifier": XGBClassifier(eval_metric='logloss', random_state=42)
                # "CatBoosting Classifier": CatBoostClassifier(verbose=False, random_seed=42),
            }

            # --- CHANGE 8: Define deeper/broader parameter distributions for RandomizedSearchCV ---
            params = {
                "Logistic Regression": {
                    'C': [0.001, 0.01, 0.1, 1, 10, 100], # Expanded range
                    'solver': ['liblinear', 'lbfgs'] # Use liblinear as it handles L1/L2 better
                },
                "XGBClassifier": {
                    'learning_rate': [0.01, 0.05, 0.1, 0.2], # Expanded range
                    'n_estimators': [100, 200, 500, 1000], # Expanded range
                    'max_depth': [3, 5, 7, 9],
                    'gamma': [0, 0.1, 0.5, 1],
                    'subsample': [0.6, 0.8, 1.0],
                }
                # "CatBoosting Classifier": {
                #     'iterations': [200, 500, 750, 1000], # Expanded range
                #     'learning_rate': [0.01, 0.03, 0.05, 0.1],
                #     'depth': [6, 8, 10], # Expanded range
                #     'l2_leaf_reg': [1, 3, 5, 7],
                #     'subsample': [0.6, 0.8, 1.0],
                # }
            }

            logging.info('Starting model evaluation using cross-validation (ROC AUC)...')
            model_report, best_models, predictions = evaluate_models(X_train, y_train, X_test, y_test, models, params, metric='roc_auc')

            best_model_name = max(model_report, key=model_report.get)
            best_model = best_models[best_model_name]
            best_model_score = model_report[best_model_name]
            
            if best_model_score < 0.6:
                raise CustomException("No model found with ROC AUC score above the threshold of 0.6", sys)
            
            logging.info(f"Best model found: {best_model_name} with ROC AUC score: {model_report[best_model_name]: .4f}")
            
            logging.info('Saving the best model to disk...')
            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )

            logging.info(f"Model saved to {self.model_trainer_config.trained_model_file_path}")

            # Save the full test array for the separate evaluation step
            logging.info("Saving test data array (features and target) for downstream evaluation pipeline...")
            np.save(self.model_trainer_config.test_array_path, test_array)
            logging.info(f"Test array saved to {self.model_trainer_config.test_array_path}")

            # Return the best model and the path to the saved test array
            return best_model_name, self.model_trainer_config.test_array_path

        except Exception as e:
            raise CustomException(e, sys)
