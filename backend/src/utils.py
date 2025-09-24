import os
import sys

import numpy as np
import pandas as pd
import dill
from sklearn.metrics import r2_score, roc_auc_score

from src.exception import CustomException
from src.logger import logging
from sklearn.model_selection import GridSearchCV

def save_object(file_path, obj):
    try:
        dir_path=os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "wb") as fle_obj:         
            dill.dump(obj, fle_obj)

    except Exception as e:
        raise CustomException(e, sys)

def evaluate_models(X_train, y_train, X_test, y_test, models: dict, params: dict, metric='roc_auc'):
    try:
        report = {}
        best_models = {}

        for model_name, model in models.items():
            logging.info(f"Starting GridSearchCV for{model_name}...")
            param_grid = params.get(model_name, {})

            # Grid Search with Cross-Validation
            gs = GridSearchCV(
                estimator=model,
                param_grid=param_grid,
                scoring=metric,
                cv=5,
                n_jobs=-1,
                verbose=0
            )

            gs.fit(X_train, y_train)
            best_model = gs.best_estimator_

            logging.info(f"Completed GridSearchCV for {model_name}. Best parameters: {gs.best_params_}")

            ## TODO: Check if statement is needed
            # Predict probabilities for ROC AUC
            if hasattr(best_model, "predict_proba"):
                y_test_pred_proba = best_model.predict_proba(X_test)[:, 1]
            else:
                y_test_pred_proba = best_model.decision_function(X_test)

            score = roc_auc_score(y_test, y_test_pred_proba)
            report[model_name] = score
            best_models[model_name] = best_model
            logging.info(f"{model_name} ROC AUC Score on test set: {score: .4f}")

        return report, best_models

    except Exception as e:
        raise CustomException(e, sys)

def load_object(file_path):
    try:
        with open(file_path, "rb") as fle_obj:
            return dill.load(fle_obj)
    except Exception as e:
        raise CustomException(e, sys)