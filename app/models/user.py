from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(
        db.Enum('admin', 'user', name='user_role_enum'),
        nullable=False, default='user')

    blood_group = db.Column(db.String(5), nullable=True)
    phone = db.Column(db.String(15), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow)

    requests = db.relationship('BloodRequest',
        backref='requester', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'
