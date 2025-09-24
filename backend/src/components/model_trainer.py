import os
import sys
from dataclasses import dataclass
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from catboost import CatBoostClassifier

from sklearn.metrics import roc_auc_score

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object, evaluate_models

@dataclass
class ModelTrainerConfig:
    trained_model_file_path=os.path.join('artifacts', 'model.pkl')

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
                "XGBClassifier": XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42),
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
            model_report, best_models = evaluate_models(X_train, y_train, X_test, y_test, models, params, metric='roc_auc')

            best_model_name = max(model_report, key=model_report.get)
            best_model = best_models[best_model_name]
            best_model_score = model_report[best_model_name]

            logging.info(f"Best model found: {best_model_name} with ROC AUC score: {best_model_score: .4f}")

            if best_model_score < 0.6:
                raise CustomException("No model found with ROC AUC score above the threshold of 0.6", sys)
            
            logging.info('Saving the best model to disk...')
            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )

            y_pred_proba = best_model.predict_proba(X_test)[:, 1]
            roc_auc = roc_auc_score(y_test, y_pred_proba)
            return roc_auc

        except Exception as e:
            raise CustomException(e, sys)