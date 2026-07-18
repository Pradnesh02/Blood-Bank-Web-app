from app import db
from datetime import datetime

class Donor(db.Model):
    __tablename__ = 'donors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=True)

    blood_group = db.Column(
        db.Enum('A+','A-','B+','B-','O+','O-','AB+','AB-',
                name='blood_group_enum'),
        nullable=False)

    last_donation_date = db.Column(db.Date, nullable=True)

    health_status = db.Column(
        db.Enum('Fit', 'Unfit', name='health_status_enum'),
        nullable=False, default='Fit')

    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f'<Donor {self.name} ({self.blood_group})>'
