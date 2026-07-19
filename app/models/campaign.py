from app import db
from datetime import datetime

class Campaign(db.Model):
    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    # City / venue where campaign will be held
    location = db.Column(db.String(300), nullable=False)

    # Full address
    address = db.Column(db.Text, nullable=True)

    campaign_date = db.Column(db.Date, nullable=False)
    campaign_time = db.Column(db.String(100), nullable=True)

    description = db.Column(db.Text, nullable=True)

    # Target blood groups needed
    target_blood_groups = db.Column(
        db.String(100), nullable=True)

    # Expected donor count target
    target_donors = db.Column(db.Integer, nullable=True)

    # Is campaign still active/upcoming
    is_active = db.Column(
        db.Boolean, nullable=False, default=True)

    # Contact person for the campaign
    organizer_name = db.Column(db.String(100), nullable=True)
    organizer_phone = db.Column(db.String(15), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow)

    def __repr__(self):
        return (f'<Campaign {self.title} '
                f'at {self.location} '
                f'on {self.campaign_date}>')
