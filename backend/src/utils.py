# In src/utils.py

import os
import sys

import numpy as np
import pandas as pd
import dill
from sklearn.metrics import r2_score, roc_auc_score

from src.exception import CustomException
from src.logger import logging
# --- CHANGE 1: Import RandomizedSearchCV and remove GridSearchCV ---
from sklearn.model_selection import RandomizedSearchCV

def save_object(file_path, obj):
    try:
        dir_path=os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "wb") as fle_obj:      
            dill.dump(obj, fle_obj)

    except Exception as e:
        raise CustomException(e, sys)

# --- CHANGE 2: Update the function to use RandomizedSearchCV ---
def evaluate_models(X_train, y_train, X_test, y_test, models: dict, params: dict, metric='roc_auc'):
    try:
        report = {}
        best_models = {}
        predictions = {}

        for model_name, model in models.items():
            # --- CHANGE 3: Update logging to reflect RandomizedSearchCV ---
            logging.info(f"Starting RandomizedSearchCV for {model_name}...")
            # param_grid now represents the distribution to sample from
            param_distributions = params.get(model_name, {})

            # Randomized Search with Cross-Validation
            gs = RandomizedSearchCV(
                estimator=model,
                param_distributions=param_distributions, # Use param_distributions for RandomizedSearchCV
                scoring=metric,
                cv=5,
                n_iter=50,  # --- CHANGE 4: Specify 50 iterations for sampling the large parameter space ---
                random_state=42, # --- CHANGE 5: Add random_state for reproducibility ---
                n_jobs=-1,
                verbose=0
            )

            gs.fit(X_train, y_train)
            best_model = gs.best_estimator_

            # --- CHANGE 6: Update logging for RandomizedSearchCV ---
            logging.info(f"Completed RandomizedSearchCV for {model_name}. Best parameters: {gs.best_params_}")

            # Predict probabilities for ROC AUC
            if hasattr(best_model, "predict_proba"):
                y_test_pred_proba = best_model.predict_proba(X_test)[:, 1]
            else:
                y_test_pred_proba = best_model.decision_function(X_test)

            y_test_pred = best_model.predict(X_test)
            score = roc_auc_score(y_test, y_test_pred_proba)
            report[model_name] = score
            best_models[model_name] = best_model
            predictions[model_name] = {'y_pred': y_test_pred, 'y_proba': y_test_pred_proba}

            logging.info(f"{model_name} ROC AUC Score on test set: {score: .4f}")

        return report, best_models, predictions

    except Exception as e:
        raise CustomException(e, sys)

def load_object(file_path):
    try:
        with open(file_path, "rb") as fle_obj:
            return dill.load(fle_obj)
    except Exception as e:
        raise CustomException(e, sys)