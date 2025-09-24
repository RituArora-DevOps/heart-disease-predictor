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
        except Exception as e:
            raise CustomException(e, sys)