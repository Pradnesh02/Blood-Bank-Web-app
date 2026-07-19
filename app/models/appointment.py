from app import db
from datetime import datetime

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)

    # Who is booking
    donor_id = db.Column(
        db.Integer,
        db.ForeignKey('donors.id', ondelete='CASCADE'),
        nullable=False)

    # Appointment details
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)

    slot = db.Column(
        db.Enum(
            'Morning (9AM-12PM)',
            'Afternoon (12PM-3PM)',
            'Evening (3PM-6PM)',
            name='appointment_slot_enum'),
        nullable=False)

    blood_group = db.Column(
        db.Enum(
            'A+','A-','B+','B-',
            'O+','O-','AB+','AB-',
            name='appointment_blood_group_enum'),
        nullable=False)

    # Units donor intends to donate (always 1 by default)
    units_to_donate = db.Column(
        db.Integer, nullable=False, default=1)

    status = db.Column(
        db.Enum(
            'Scheduled',
            'Completed',
            'Cancelled',
            'No Show',
            name='appointment_status_enum'),
        nullable=False,
        default='Scheduled')

    # Notes from donor
    notes = db.Column(db.Text, nullable=True)

    # When stock was updated (set when status → Completed)
    stock_updated_at = db.Column(
        db.DateTime(timezone=True), nullable=True)

    # Units actually donated (set on completion)
    units_donated = db.Column(
        db.Integer, nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow)

    # Relationship back to donor
    donor = db.relationship(
        'Donor',
        backref=db.backref('appointments', lazy=True))

    def __repr__(self):
        return (f'<Appointment donor={self.donor_id} '
                f'date={self.appointment_date} '
                f'status={self.status}>')
