from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

# Base class for declarative class definitions
Base = declarative_base()

class UserAssessment(Base):
    """
    SQLAlchemy model for logging every prediction made by the API.
    """
    __tablename__ = 'user_assessments'

    # Primary Key and Timestamp (Audit/Tracking)
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Input Data (For Model Drift & Retraining)
    # Using JSON type to store the complex dictionary of 22 user inputs
    user_inputs_json = Column(JSON, nullable=False) 
    
    # Prediction Results (The Model's Output)
    prediction_probability = Column(Float, nullable=False) # The raw score, e.g., 0.1919
    prediction_result = Column(Boolean, nullable=False)    # The final prediction (True/False for Heart Disease)
    
    def __repr__(self):
        return f"Assessment(id={self.id}, prob={self.prediction_probability})"