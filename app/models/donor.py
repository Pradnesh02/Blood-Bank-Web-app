from app import db
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

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

    # ── NEW FIELD ──────────────────────────────────────
    weight = db.Column(db.Float, nullable=True)
    # Weight in kilograms
    # Eligibility rule: weight >= 50 kg → eligible
    # ───────────────────────────────────────────────────

    health_status = db.Column(
        db.Enum('Fit', 'Unfit', name='health_status_enum'),
        nullable=False, default='Fit')

    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), default=datetime.utcnow)

    # ── COMPUTED PROPERTIES ────────────────────────────

    @property
    def next_donation_date(self):
        """
        Returns the next eligible donation date.
        Rule: 6 months after last donation.
        Returns None if never donated.
        """
        if self.last_donation_date:
            return (self.last_donation_date + relativedelta(months=6))
        return None

    @property
    def is_weight_eligible(self):
        """
        Returns True if donor weight >= 50 kg.
        Returns None if weight not recorded.
        """
        if self.weight is None:
            return None
        return self.weight >= 50.0

    @property
    def days_until_eligible(self):
        """
        Returns number of days until donor can
        donate again. Negative means already eligible.
        """
        if self.next_donation_date:
            delta = self.next_donation_date - date.today()
            return delta.days
        return None

    @property
    def is_date_eligible(self):
        """
        True if today >= next_donation_date
        or if never donated before.
        """
        if self.next_donation_date is None:
            return True
        return date.today() >= self.next_donation_date

    @property
    def is_fully_eligible(self):
        """
        True only if BOTH weight AND date eligible.
        """
        return (self.is_weight_eligible is True and self.is_date_eligible)

    def __repr__(self):
        return f'<Donor {self.name} ({self.blood_group})>'
