import sys
import os
import numpy as np
from dataclasses import dataclass
from src.exception import CustomException
from src.logger import logging
from src.utils import load_object
# Import the component utility functions
from src.components.model_evaluator import evaluate_model_performance
from src.components.threshold_tuner import tune_threshold

@dataclass
class ModelEvaluatorConfig:
    # Paths to load artifacts saved by model_trainer
    trained_model_file_path: str = os.path.join('artifacts', 'model.pkl')
    test_array_path: str = os.path.join('artifacts', 'test_array.npy')

    # Paths to save evaluation artifacts
    metrics_file_path: str = os.path.join('artifacts', 'model_metrics.txt')
    threshold_cuve_path: str = os.path.join('artifacts', 'precision_recall_threshold_curve.png')
    threshold_metrics_path: str = os.path.join('artifacts', 'model_threshold_metrics.txt')
    # Path to save the final optimal threshold value used by the FastAPI service
    optimal_threshold_path: str = os.path.join('artifacts', 'optimal_threshold.txt')

class ModelEvaluator:
    def __init__(self):
        self.config = ModelEvaluatorConfig()

    def initiate_evaluation(self):
        try:
            logging.info("Starting separate Model Evaluation and Threshold Tuning pipeline.")
            
            # 1. Load the saved model and test array
            logging.info(f"Loading best model from {self.config.trained_model_file_path}")
            model = load_object(self.config.trained_model_file_path)
            
            logging.info(f"Loading test array from {self.config.test_array_path}")
            test_array = np.load(self.config.test_array_path)

            # Split features and target
            X_test, y_test = test_array[:, :-1], test_array[:, -1]

            # 2. Generate predictions and probabilities
            logging.info("Generating predictions using the best model...")
            y_pred_proba = model.predict_proba(X_test)[:, 1] 
            y_pred_default = (y_pred_proba >= 0.5).astype(int)

            # 3. Evaluate model performance at default threshold (0.5)
            logging.info("Evaluating model performance at default threshold (0.5)...")
            # We discard the return value here as we only need the side effect (writing the file)
            _ = evaluate_model_performance(
                y_test, 
                y_pred_default, 
                y_pred_proba, 
                self.config.metrics_file_path
            )

            # 4. Tune threshold and save the tuning report/plot
            logging.info("Starting threshold tuning to maximize F1 score...")
            optimal_threshold, best_f1, _ = tune_threshold(
                y_test, 
                y_pred_proba, 
                self.config.threshold_cuve_path,
                self.config.threshold_metrics_path
            )

            # 5. Save the optimal threshold for the prediction pipeline
            logging.info(f"Saving optimal threshold ({optimal_threshold:.4f}) to {self.config.optimal_threshold_path}")
            with open(self.config.optimal_threshold_path, 'w') as f:
                f.write(f"{optimal_threshold:.6f}") # Save with high precision

            logging.info(f"Evaluation pipeline completed. Optimal threshold: {optimal_threshold:.4f}, F1 Score: {best_f1:.4f}")
            
            return optimal_threshold

        except Exception as e:
            raise CustomException(e, sys)

if __name__ == '__main__':
    # This block allows running the evaluation separately after training
    try:
        evaluator = ModelEvaluator()
        optimal_t = evaluator.initiate_evaluation()
        print(f"\nOptimal Deployment Threshold: {optimal_t:.4f}")
    except CustomException as e:
        print(f"Evaluation failed: {e}")
