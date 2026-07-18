# from sklearn.ensemble import RandomForestClassifier (lazy-loaded inside function)
import numpy as np
from datetime import datetime

# Global model cache to avoid retraining on every query
_model_cache = None

def train_eligibility_model():
    """
    Trains a RandomForest model on synthetic donor records.
    Features: [age, days_since_last_donation, health_status_fit]
    Rules for class 1 (Eligible):
    - Age 18-65
    - days_since >= 90
    - health_status == 'Fit'
    Includes 3% noise to simulate confidence variance.
    """
    from sklearn.ensemble import RandomForestClassifier
    np.random.seed(42)
    X = []
    y = []
    for _ in range(1000):
        age = np.random.randint(15, 75)
        days_since = np.random.randint(10, 200)
        health_fit = np.random.choice([0, 1], p=[0.15, 0.85])
        
        # Rule check
        is_eligible = 1 if (18 <= age <= 65 and days_since >= 90 and health_fit == 1) else 0
        
        # Add slight noise (3%)
        if np.random.rand() < 0.03:
            is_eligible = 1 - is_eligible
            
        X.append([age, days_since, health_fit])
        y.append(is_eligible)
        
    clf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
    clf.fit(X, y)
    return clf

def get_or_train_eligibility_model():
    global _model_cache
    if _model_cache is None:
        _model_cache = train_eligibility_model()
    return _model_cache

def get_ineligibility_reason(donor, days_since):
    reasons = []
    if not (18 <= donor.age <= 65):
        reasons.append(f"Age {donor.age} is outside the eligible range (18-65)")
    if days_since < 90:
        reasons.append(f"{90 - days_since} days remaining until 90-day donation window closes")
    if donor.health_status != 'Fit':
        reasons.append("Health status is not registered as 'Fit'")
    return " & ".join(reasons) if reasons else "ML model output flag"

def predict_donor_eligibility(donor):
    """
    Predicts if a donor is currently eligible.
    Returns: {'eligible': True/False, 'confidence': 0.87, 'reason': ...}
    """
    # Calculate days since last donation date
    # handle cases where donor.last_donation_date is datetime or date
    last_date = donor.last_donation_date
    if isinstance(last_date, datetime):
        last_date = last_date.date()
        
    days_since = (datetime.utcnow().date() - last_date).days
    
    # Feature vector: [age, days_since, is_fit]
    is_fit = 1 if donor.health_status == 'Fit' else 0
    features = np.array([[donor.age, days_since, is_fit]])
    
    model = get_or_train_eligibility_model()
    prediction = model.predict(features)[0]
    confidence = model.predict_proba(features)[0].max()
    
    eligible = bool(prediction == 1)
    reason = None
    if not eligible:
        reason = get_ineligibility_reason(donor, days_since)
        
    return {
        'eligible': eligible,
        'confidence': round(float(confidence), 2),
        'reason': reason
    }
