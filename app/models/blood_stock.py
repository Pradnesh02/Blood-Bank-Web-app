from app import db
from datetime import datetime

class BloodStock(db.Model):
    __tablename__ = 'blood_stock'

    id = db.Column(db.Integer, primary_key=True)

    blood_group = db.Column(
        db.Enum('A+','A-','B+','B-','O+','O-','AB+','AB-',
                name='blood_group_stock_enum'),
        unique=True, nullable=False)

    units = db.Column(db.Integer, nullable=False, default=0)

    last_updated = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<BloodStock {self.blood_group}: {self.units} units>'
