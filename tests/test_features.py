import pytest
from datetime import date, timedelta, time
from app import db, bcrypt
from app.models.user import User
from app.models.donor import Donor
from app.models.appointment import Appointment
from app.models.campaign import Campaign
from app.models.blood_stock import BloodStock

def register_and_login(client, email="test@bloodbank.com", password="testpassword", role="user"):
    # Clear existing user if any
    User.query.filter_by(email=email).delete()
    db.session.commit()

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(
        name="Test User",
        email=email,
        phone="5550001",
        blood_group="O+",
        password_hash=hashed_pw,
        role=role
    )
    db.session.add(user)
    db.session.commit()

    # Log in
    response = client.post('/auth/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)
    return user

# ── 1. Weight Eligibility Tests ──
def test_weight_eligibility_properties():
    # Eligible donor (>= 50kg)
    d1 = Donor(name="Eligible", age=30, phone="123", blood_group="A+", weight=65.0)
    assert d1.is_weight_eligible is True

    # Ineligible donor (< 50kg)
    d2 = Donor(name="Ineligible", age=30, phone="124", blood_group="A+", weight=45.0)
    assert d2.is_weight_eligible is False

    # Pending donor (weight not recorded)
    d3 = Donor(name="Pending", age=30, phone="125", blood_group="A+", weight=None)
    assert d3.is_weight_eligible is None

# ── 2. Next Donation Date Highlighter Tests ──
def test_next_donation_date_properties():
    # First time donor (last_donation_date is None)
    d1 = Donor(name="First Time", age=30, phone="123", blood_group="B-", last_donation_date=None)
    assert d1.next_donation_date is None
    assert d1.is_date_eligible is True
    assert d1.days_until_eligible is None

    # Donated 7 months ago (eligible now)
    last_date_eligible = date.today() - timedelta(days=210)
    d2 = Donor(name="Eligible", age=30, phone="124", blood_group="B-", last_donation_date=last_date_eligible)
    assert d2.is_date_eligible is True
    assert d2.days_until_eligible < 0

    # Donated 2 months ago (ineligible now)
    last_date_ineligible = date.today() - timedelta(days=60)
    d3 = Donor(name="Ineligible", age=30, phone="125", blood_group="B-", last_donation_date=last_date_ineligible)
    assert d3.is_date_eligible is False
    assert d3.days_until_eligible > 0

# ── 3. Appointment Booking System Tests ──
def test_appointment_booking_flow(client, app):
    with app.app_context():
        # Setup users and donors
        admin = register_and_login(client, email="admin@bloodbank.com", password="adminpassword", role="admin")
        
        eligible_donor = Donor(name="Eligible Donor", age=25, phone="555111", blood_group="O-", weight=60.0)
        ineligible_donor = Donor(name="Ineligible Donor", age=25, phone="555222", blood_group="O-", weight=45.0)
        
        db.session.add(eligible_donor)
        db.session.add(ineligible_donor)
        db.session.commit()

        # Try booking for ineligible donor (weight under 50kg)
        resp = client.post('/appointments/book', data={
            'donor_id': ineligible_donor.id,
            'appointment_date': str(date.today() + timedelta(days=2)),
            'slot': 'Morning (9AM-12PM)',
            'notes': 'Test notes'
        }, follow_redirects=True)
        assert b"weighs 45.0kg which is below the minimum 50kg requirement" in resp.data

        # Book for eligible donor
        appt_date = date.today() + timedelta(days=2)
        resp = client.post('/appointments/book', data={
            'donor_id': eligible_donor.id,
            'appointment_date': str(appt_date),
            'slot': 'Morning (9AM-12PM)',
            'notes': 'Test notes'
        }, follow_redirects=True)
        assert b"Appointment booked successfully" in resp.data

        # Verify database record
        appt = Appointment.query.filter_by(donor_id=eligible_donor.id).first()
        assert appt is not None
        assert appt.status == 'Scheduled'
        assert appt.blood_group == 'O-'

# ── 4. Appointment Completion & Stock Update Tests ──
def test_appointment_completion_flow(client, app):
    with app.app_context():
        admin = register_and_login(client, email="admin2@bloodbank.com", password="adminpassword", role="admin")
        
        donor = Donor(name="Completion Donor", age=30, phone="555333", blood_group="AB+", weight=70.0)
        db.session.add(donor)
        db.session.commit()

        appt = Appointment(
            donor_id=donor.id,
            appointment_date=date.today(),
            appointment_time=time(12, 0),
            slot='Afternoon (12PM-3PM)',
            blood_group=donor.blood_group,
            status='Scheduled'
        )
        db.session.add(appt)
        db.session.commit()

        # Record initial stock
        initial_stock = BloodStock.query.filter_by(blood_group="AB+").first()
        initial_units = initial_stock.units if initial_stock else 0

        # Mark completed via POST route
        resp = client.post(f'/appointments/{appt.id}/complete', data={
            'units_donated': 2
        })
        assert resp.status_code == 200
        
        # Verify status and donor update
        db.session.refresh(appt)
        db.session.refresh(donor)
        assert appt.status == 'Completed'
        assert appt.units_donated == 2
        assert donor.last_donation_date == date.today()

        # Verify inventory update
        stock = BloodStock.query.filter_by(blood_group="AB+").first()
        assert stock.units == initial_units + 2

# ── 5. Campaign Notices Board Tests ──
def test_campaigns_board_flow(client, app):
    with app.app_context():
        # Clean existing campaigns
        Campaign.query.delete()
        db.session.commit()

        # Add mock campaign drive
        c_date = date.today() + timedelta(days=10)
        c = Campaign(
            title="City Donation Drive",
            location="Central Hall",
            address="1 Plaza Avenue",
            campaign_date=c_date,
            campaign_time="10AM - 4PM",
            target_blood_groups="O+,O-,A+",
            is_active=True
        )
        db.session.add(c)
        db.session.commit()

        # Assert campaign details render in notices list
        resp = client.get('/campaigns/')
        assert resp.status_code == 200
        assert b"City Donation Drive" in resp.data
        assert b"Central Hall" in resp.data

        # Verify api returns next campaign details
        resp = client.get('/campaigns/api/next')
        assert resp.status_code == 200
        data = resp.json
        assert data['campaign']['title'] == "City Donation Drive"
        assert data['campaign']['days_away'] == 10
