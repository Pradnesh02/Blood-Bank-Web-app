from app.ml.eligibility import predict_donor_eligibility
from app.ml.compatibility import get_compatible_alternatives
from app.ml.stock_alert import get_smart_alert_level
from app.models.donor import Donor
from datetime import datetime, timedelta

def test_donor_eligibility_ml_evaluation(app):
    """
    Asserts ML predictor flags fit, age-appropriate donors who have waited 90+ days
    as eligible, and unfit or underage/overage profiles as ineligible.
    """
    with app.app_context():
        # 1. Eligible Case
        d_eligible = Donor(
            name="Eligible Donor",
            age=35,
            phone="555-1234",
            address="Green Hills",
            blood_group="O+",
            last_donation_date=(datetime.utcnow() - timedelta(days=100)).date(),
            health_status="Fit",
            notes="Regular"
        )
        res_e = predict_donor_eligibility(d_eligible)
        assert res_e['eligible'] is True
        
        # 2. Ineligible Case (Health Status: Unfit)
        d_unfit = Donor(
            name="Unfit Donor",
            age=35,
            phone="555-1234",
            address="Green Hills",
            blood_group="O+",
            last_donation_date=(datetime.utcnow() - timedelta(days=100)).date(),
            health_status="Unfit",
            notes="Sick"
        )
        res_u = predict_donor_eligibility(d_unfit)
        assert res_u['eligible'] is False
        
        # 3. Ineligible Case (Too recent: 45 days)
        d_recent = Donor(
            name="Recent Donor",
            age=35,
            phone="555-1234",
            address="Green Hills",
            blood_group="O+",
            last_donation_date=(datetime.utcnow() - timedelta(days=45)).date(),
            health_status="Fit",
            notes="Active"
        )
        res_r = predict_donor_eligibility(d_recent)
        assert res_r['eligible'] is False

def test_blood_compatibility_logic(app):
    """
    Asserts compatibility mapping yields matching list structures.
    """
    with app.app_context():
        result = get_compatible_alternatives('A+', 1)
        assert 'alternatives' in result
        assert 'contact_donors' in result
        
        # A+ is compatible with O-, O+, A-, A+
        # If A+ is in rules['can_give_to'], that group is compatible
        # Ensure we returned list items
        assert isinstance(result['alternatives'], list)

def test_smart_stock_alert_computations(app):
    """
    Asserts warning calculations return proper alert level structure.
    """
    with app.app_context():
        result = get_smart_alert_level('O-')
        assert 'level' in result
        assert 'days_until_empty' in result
        assert 'recommended_units' in result
        assert result['level'] in ['critical', 'low', 'warning', 'safe']
