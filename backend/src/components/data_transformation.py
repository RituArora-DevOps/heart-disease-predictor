import os
import sys
import numpy as np
import pandas as pd
from dataclasses  import dataclass

from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin

from src.logger import logging
from src.exception import CustomException
from src.utils import save_object

@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path=os.path.join('artifacts', 'preprocessor.pkl')

class BinaryEncoder(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.mapping = {'Yes': 1, 'No': 0}
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        return X.replace(self.mapping).astype(int)
    
class DataTransformation:
    def __init__(self):
        self.config=DataTransformationConfig()
    
    def get_preprocessor(self):
        try:
            logging.info("Preparing preprocessing pipelines for both numerical and categorical data")

            # Binary features still in object type
            binary_cols = ['Exercise', 'Skin_Cancer', 'Other_Cancer',
                        'Depression', 'Arthritis', 'Smoking_History']

            # Categorical Ordinal features
            ordinal_cols = ['General_Health', 'Checkup', 'Age_Category', 'Sex', 'Diabetes']

            # Custom order for ordinal encoder
            ordinal_mapping = [
                ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'],             # General_Health
                ['Never', '5 or more years ago', 'Within the past 5 years',
                'Within the past 2 years', 'Within the past year'],            # Checkup
                ['18-24', '25-29', '30-34', '35-39', '40-44',
                '45-49', '50-54', '55-59', '60-64', '65-69',
                '70-74', '75-79', '80+'],                                      # Age_Category
                ['Female', 'Male'],                                             # Sex
                ['No', 'No, pre-diabetes or borderline diabetes',
                'Yes, but female told only during pregnancy', 'Yes']           # Diabetes
            ]

            # Numerical columns (already include log-transformed ones)
            num_cols = [
                'Height_(cm)', 'Weight_(kg)', 'BMI', 'Alcohol_Consumption',
                'Fruit_Consumption', 'Green_Vegetables_Consumption', 'FriedPotato_Consumption',
                'Weight_(kg)_log', 'BMI_log', 'Alcohol_Consumption_log', 'Fruit_Consumption_log',
                'Green_Vegetables_Consumption_log', 'FriedPotato_Consumption_log'
            ]

            # Pipeline for numeric data
            num_pipeline = Pipeline([
                ('scaler', StandardScaler())
            ])

            # Pipeline for binary categorical data
            binary_pipeline = Pipeline([
                ('binary_encoder', BinaryEncoder())
            ])

            # Pipeline for ordinal features
            ordinal_pipeline = Pipeline([
                ('ordinal_encoder', OrdinalEncoder(categories=ordinal_mapping))
            ])

            # Full preprocessor
            preprocessor = ColumnTransformer([  # column transformer is a transformer that allows you to combine multiple transformers
                ('num', num_pipeline, num_cols),
                ('bin', binary_pipeline, binary_cols),
                ('ord', ordinal_pipeline, ordinal_cols)
            ])

            return preprocessor
        
        except Exception as e:
            raise CustomException(e, sys)
        
    def initiate_data_transformation(self, train_path, test_path):
        try:
            logging.info("Starting data transformation")
            # Reading train and test data
            train_df=pd.read_csv(train_path)
            test_df=pd.read_csv(test_path)

            logging.info("Read train and test data completed")

            # Target encoding
            target_col = 'Heart_Disease'
            train_df[target_col]=train_df[target_col].map({'Yes':1, 'No':0})
            test_df[target_col]=test_df[target_col].map({'Yes':1, 'No':0})

            logging.info("Target column encoding completed")

            logging.info("Split input and target features")
            # Splitting input and target features
            X_train = train_df.drop(columns=[target_col], axis=1)
            y_train = train_df[target_col]

            X_test = test_df.drop(columns=[target_col], axis=1)
            y_test = test_df[target_col]

            preprocessor = self.get_preprocessor()

            logging.info("Fitting preprocessor on training data")
            # Fitting preprocessor
            preprocessor.fit(X_train)

            logging.info("Transforming training and testing data")
            # Transforming training and testing data
            X_train_preprocessed = preprocessor.transform(X_train)
            X_test_preprocessed = preprocessor.transform(X_test)

            logging.info("Saving preprocessor")
            # Saving preprocessor object
            save_object(self.config.preprocessor_obj_file_path, preprocessor) 

            logging.info("Data transformation completed")

            return (
                np.hstack((X_train_preprocessed, y_train.values.reshape(-1, 1))), 
                np.hstack((X_test_preprocessed, y_test.values.reshape(-1, 1))), 
                self.config.preprocessor_obj_file_path
            )

        except Exception as e:
            raise CustomException(e, sys)