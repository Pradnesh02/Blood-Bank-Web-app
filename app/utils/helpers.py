import random
from datetime import datetime, timedelta
from app import db
from app.models.donor import Donor
from app.models.request import BloodRequest
from app.models.user import User

def seed_historical_data():
    """
    Seeds synthetic donors, users, stock holdings, and requests
    so that reports and forecasting models function instantly with realistic curves.
    """
    blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
    
    # 1. Seed regular users for requests relation
    users = []
    for i in range(1, 6):
        email = f"user{i}@bloodbank.com"
        existing = User.query.filter_by(email=email).first()
        if not existing:
            from app import bcrypt
            hashed_pw = bcrypt.generate_password_hash("user123").decode('utf-8')
            u = User(
                name=f"Regular User {i}",
                email=email,
                phone=f"55501000{i}",
                blood_group=random.choice(blood_groups),
                password_hash=hashed_pw,
                role='user'
            )
            db.session.add(u)
            users.append(u)
        else:
            users.append(existing)
    db.session.commit()
    
    # 2. Seed Donor registry
    if Donor.query.count() == 0:
        names = [
            "John Doe", "Jane Smith", "Michael Campbell", "Sarah Connor",
            "Peter Parker", "Bruce Wayne", "Clark Kent", "Diana Prince",
            "Tony Stark", "Steve Rogers", "Natasha Romanoff", "Wanda Maximoff"
        ]
        for i, name in enumerate(names):
            # 85% Fit, 15% Unfit
            health = 'Fit' if random.random() > 0.15 else 'Unfit'
            d = Donor(
                name=name,
                age=random.randint(18, 65),
                phone=f"55502000{i:02d}",
                address=f"{random.randint(100, 999)} Metro Parkway, City",
                blood_group=random.choice(blood_groups),
                last_donation_date=(datetime.utcnow() - timedelta(days=random.randint(15, 200))).date(),
                health_status=health,
                notes="Registered during standard site onboarding."
            )
            db.session.add(d)
        db.session.commit()

    # 3. Seed BloodStock with initial units (e.g. between 6 and 18)
    # Since first run initializes all to 0, let's bump them to make it look active
    from app.models.blood_stock import BloodStock
    for stock in BloodStock.query.all():
        if stock.units == 0:
            stock.units = random.randint(6, 18)
    db.session.commit()

    # 4. Seed Requests History (40-60 requests over last 30 days)
    if BloodRequest.query.count() == 0:
        hospitals = ["Mercy General", "St. Jude Hospital", "City Medical Center", "County Memorial"]
        urgencies = ["Normal", "Urgent", "Emergency"]
        statuses = ["Approved", "Rejected", "Pending"]
        
        # We need a range of dates in the last 30 days to build a timeseries
        base_date = datetime.utcnow()
        for i in range(60):
            req_date = base_date - timedelta(days=random.randint(0, 30), hours=random.randint(1, 23))
            qty = random.randint(1, 4)
            bg = random.choice(blood_groups)
            
            req = BloodRequest(
                requester_name=f"Requester {i}",
                blood_group=bg,
                quantity=qty,
                hospital_name=random.choice(hospitals),
                urgency=random.choice(urgencies),
                required_date=(req_date + timedelta(days=random.randint(1, 3))).date(),
                notes="Onboarded via historical database imports.",
                status=random.choice(statuses),
                user_id=random.choice(users).id,
                created_at=req_date
            )
            db.session.add(req)
        db.session.commit()
