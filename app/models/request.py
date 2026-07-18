from app import db
from datetime import datetime

class BloodRequest(db.Model):
    __tablename__ = 'blood_requests'

    id = db.Column(db.Integer, primary_key=True)
    requester_name = db.Column(db.String(100), nullable=False)

    blood_group = db.Column(
        db.Enum('A+','A-','B+','B-','O+','O-','AB+','AB-',
                name='blood_group_request_enum'),
        nullable=False)

    quantity = db.Column(db.Integer, nullable=False, default=1)

    hospital_name = db.Column(db.String(200), nullable=True)

    urgency = db.Column(
        db.Enum('Normal', 'Urgent', 'Emergency',
                name='urgency_enum'),
        nullable=False, default='Normal')

    required_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    status = db.Column(
        db.Enum('Pending', 'Approved', 'Rejected',
                name='request_status_enum'),
        nullable=False, default='Pending')

    user_id = db.Column(db.Integer,
        db.ForeignKey('users.id'), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint('quantity >= 1 AND quantity <= 10',
                           name='check_quantity_range'),
    )

    def __repr__(self):
        return f'<BloodRequest {self.blood_group} x{self.quantity}>'
