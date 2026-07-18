from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.request import BloodRequest
from app.models.blood_stock import BloodStock
from app import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Renders user dashboard with request status cards and recent histories.
    """
    total_requests = BloodRequest.query.filter_by(user_id=current_user.id).count()
    approved_requests = BloodRequest.query.filter_by(user_id=current_user.id, status='Approved').count()
    pending_requests = BloodRequest.query.filter_by(user_id=current_user.id, status='Pending').count()
    
    recent_requests = BloodRequest.query.filter_by(user_id=current_user.id).order_by(BloodRequest.id.desc()).limit(5).all()
    
    return render_template(
        'user/dashboard.html',
        total_requests=total_requests,
        approved_requests=approved_requests,
        pending_requests=pending_requests,
        recent_requests=recent_requests
    )

@user_bp.route('/request_blood')
@login_required
def request_blood():
    """
    Renders the blood request form.
    """
    blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
    return render_template('user/request_blood.html', blood_groups=blood_groups)
