# Assume 'session' is an active SQLAlchemy database session
# Assume 'raw_data' is the dictionary of 17 user inputs from the Frontend
# Assume 'probability' and 'prediction' are the model's output
from fastapi import HTTPException
from database.db_schema import UserAssessment  # SQLAlchemy model for the assessments table
from typing import Dict

def log_assessment(session, raw_data: Dict, probability: float, prediction: bool):
    """
    Creates a new database record for auditing and monitoring purposes.
    """
    # 1. Create a new Assessment object
    new_log = UserAssessment(
        user_inputs_json=raw_data,
        prediction_probability=probability,
        prediction_result=prediction
    )
    
    # 2. Add to the session and commit (make it permanent)
    try:
        session.add(new_log)
        session.commit()

    except Exception as e:
        # 3. CRITICAL: Roll back the session if the commit fails 
        #    to prevent session errors on subsequent calls.
        session.rollback()
                # Logging FAILURE: Raise an HTTP exception to fail the user request
        # and ensure the user knows the audit log failed.
        raise HTTPException(
            status_code=500, 
            detail="Prediction logged successfully, but database auditing failed."
        )


# --- DEMONSTRATION ---
# After the model predicts:
# probability = 0.155
# prediction = False (since 0.155 < 0.1919 threshold)
# log_assessment(db_session, user_input_dict, probability, prediction)