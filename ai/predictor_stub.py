# ai/predictor_stub.py
"""
AI predictor stub for compliance risk scoring.
This is a placeholder: train a real model offline and store joblib/pickle in ai/models/.
"""

import os
from pathlib import Path
import pandas as pd

MODEL_PATH = Path("ai/models/compliance_model.pkl")

def load_model():
    if MODEL_PATH.exists():
        import joblib
        return joblib.load(MODEL_PATH)
    return None

def predict_risk_from_dataframe(df: pd.DataFrame):
    """
    If model exists, returns risk scores. Otherwise returns empty list.
    """
    model = load_model()
    if model is None:
        return []
    # Expect model.predict_proba exists
    probs = model.predict_proba(df)[:,1]
    return probs.tolist()