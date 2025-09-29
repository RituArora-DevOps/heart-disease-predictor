import os
import sys
import numpy as np
import pandas as pd
from src.utils import load_object
from src.components.model_evaluator import evaluate_model_performance
from src.components.threshold_tuner import tune_threshold
from src.logger import logging
from src.exception import CustomException

if __name__ == "__main__":
    try:
        # Define paths
        model_path = os.path.join('artifacts', 'model.pkl')
        preprocessor_path = os.path.join('artifacts', 'preprocessor.pkl')
        test_data_path = os.path.join('artifacts', 'test.csv')
        metrics_output_path = os.path.join('artifacts', 'model_metrics.txt')
        threshold_curve_path = os.path.join('artifacts', 'precision_recall_threshold_curve.png')
        threshold_metrics_path = os.path.join('artifacts', 'model_threshold_metrics.txt')

        # Load objects
        logging.info("Loading model and preprocessor...")
        model = load_object(model_path)
        preprocessor = load_object(preprocessor_path)

        # Load test data
        logging.info("Loading test data...")
        df_test = pd.read_csv(test_data_path)
        X_test = df_test.drop(columns=['Heart_Disease'])
        y_test = df_test['Heart_Disease'].map({'Yes': 1, 'No': 0})

        # Preprocess test data
        logging.info("Preprocessing test data...")
        X_test_transformed = preprocessor.transform(X_test)

        # Get predictions
        logging.info("Generating predictions...")
        y_pred = model.predict(X_test_transformed)
        y_proba = model.predict_proba(X_test_transformed)[:, 1]

        # Evaluate model at default threshold (0.5)
        logging.info("Evaluating model performance at threshold 0.5...")
        evaluate_model_performance(y_test, y_pred, y_proba, metrics_output_path)

        # Tune threshold
        logging.info("Tuning threshold...")
        tune_threshold(
            y_test=y_test,
            y_proba=y_proba,
            curve_path=threshold_curve_path,
            report_path=threshold_metrics_path
        )

    except Exception as e:
        raise CustomException(e, sys)
