from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.models.donor import Donor
from app.models.blood_stock import BloodStock
from app.models.request import BloodRequest
from app import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
def restrict_to_admin():
    """
    Blocks access to non-admin users.
    """
    if current_user.role != 'admin':
        abort(403)

@admin_bp.route('/dashboard')
def dashboard():
    """
    Renders the Admin Dashboard with initial summary counts and stock objects.
    Detailed ML charts and actions will interact asynchronously.
    """
    total_donors = Donor.query.count()
    total_units = db.session.query(db.func.sum(BloodStock.units)).scalar() or 0
    pending_requests = BloodRequest.query.filter_by(status='Pending').count()
    critical_groups_count = BloodStock.query.filter(BloodStock.units < 5).count()
    
    # Last 10 requests for the dashboard table
    recent_requests = BloodRequest.query.order_by(BloodRequest.id.desc()).limit(10).all()
    
    # Blood stock list to generate grid cards
    stock_levels = BloodStock.query.order_by(BloodStock.blood_group).all()
    
    from app.ml.stock_alert import get_smart_alert_level
    stock_alerts = {s.blood_group: get_smart_alert_level(s.blood_group) for s in stock_levels}
    
    return render_template(
        'admin/dashboard.html',
        total_donors=total_donors,
        total_units=total_units,
        pending_requests=pending_requests,
        critical_groups_count=critical_groups_count,
        recent_requests=recent_requests,
        stock_levels=stock_levels,
        stock_alerts=stock_alerts
    )
