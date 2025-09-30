from fastapi import HTTPException
from database.db_schema import UserAssessment
from typing import Dict
import numpy as np  # add this import

def log_assessment(session, raw_data: Dict, probability: float, prediction: bool):
    from pprint import pprint
    print("---- LOGGING INPUT TO DB ----")
    pprint(raw_data)
    print("Probability:", probability)
    print("Prediction:", prediction)

    # 💡 Convert all NumPy types to native Python types
    clean_data = {
        key: (
            float(value) if isinstance(value, (np.floating,)) else
            int(value) if isinstance(value, (np.integer,)) else
            value
        )
        for key, value in raw_data.items()
    }

    # Also cast probability just in case
    probability = float(probability)

    new_log = UserAssessment(
        user_inputs_json=clean_data,
        prediction_probability=probability,
        prediction_result=prediction
    )

    try:
        session.add(new_log)
        session.commit()
        print(" Assessment logged successfully.")
    except Exception as e:
        session.rollback()
        print(" Error while logging assessment to DB:", str(e))
        raise HTTPException(
            status_code=500,
            detail="Prediction logged successfully, but database auditing failed."
        )
