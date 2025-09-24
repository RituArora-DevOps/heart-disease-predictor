import os
import sys

import numpy as np
import pandas as pd
import dill
from sklearn.metrics import r2_score

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
            logging.info(f"Evaluating model: {model_name}")
            param_grid = params.get(model_name, {})

    except Exception as e:
        raise CustomException(e, sys)

def load_object(file_path):
    try:
        with open(file_path, "rb") as fle_obj:
            return dill.load(fle_obj)
    except Exception as e:
        raise CustomException(e, sys)