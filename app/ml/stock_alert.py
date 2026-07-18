from app.models.blood_stock import BloodStock
from app.models.request import BloodRequest
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func

def get_average_daily_demand(blood_group):
    """
    Returns average units requested per day over the last 30 days.
    """
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    result = db.session.query(func.sum(BloodRequest.quantity)).filter(
        BloodRequest.blood_group == blood_group,
        BloodRequest.created_at >= thirty_days_ago
    ).scalar()
    
    total_requested = float(result) if result is not None else 0.0
    return max(0.1, total_requested / 30.0)

def get_pending_requests_quantity(blood_group):
    """
    Returns the sum of units in pending requests.
    """
    result = db.session.query(func.sum(BloodRequest.quantity)).filter(
        BloodRequest.blood_group == blood_group,
        BloodRequest.status == 'Pending'
    ).scalar()
    return int(result) if result is not None else 0

def get_smart_alert_level(blood_group):
    """
    Evaluates stock level flags: critical, low, warning, or safe.
    Calculates days until stock depletion and recommends restock targets.
    """
    stock = BloodStock.query.filter_by(blood_group=blood_group).first()
    if not stock:
        return {
            'level': 'safe',
            'days_until_empty': 999.0,
            'effective_stock': 0,
            'message': 'No inventory database entries found.',
            'recommended_units': 10
        }
        
    avg_daily_demand = get_average_daily_demand(blood_group)
    pending_quantity = get_pending_requests_quantity(blood_group)
    
    effective_stock = stock.units - pending_quantity
    
    if effective_stock <= 0:
        days_until_empty = 0.0
    else:
        # Avoid division by zero through max filter in avg_daily_demand
        days_until_empty = effective_stock / avg_daily_demand

    if effective_stock <= 0 or days_until_empty <= 1.0:
        level = 'critical'
        message = f"CRITICAL: {blood_group} is depleted or will run out in {round(days_until_empty, 1)} days."
    elif days_until_empty <= 3.0:
        level = 'low'
        message = f"LOW: {blood_group} stock is running low. Depletion in {round(days_until_empty, 1)} days."
    elif days_until_empty <= 7.0:
        level = 'warning'
        message = f"WARNING: {blood_group} is estimated to deplete in {round(days_until_empty, 1)} days."
    else:
        level = 'safe'
        message = f"SAFE: Sufficient stock. Estimated depletion in {round(days_until_empty, 1)} days."
        
    # Recommend 14 days of stock
    recommended_units = max(10, int(round(avg_daily_demand * 14)))
    
    return {
        'level': level,
        'days_until_empty': round(days_until_empty, 1),
        'effective_stock': effective_stock,
        'message': message,
        'recommended_units': recommended_units
    }
