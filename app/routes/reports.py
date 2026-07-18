from flask import Blueprint, render_template, send_file, jsonify, abort
from flask_login import login_required, current_user
from app.models.blood_stock import BloodStock
from app.models.donor import Donor
from app.models.request import BloodRequest
from app.utils.pdf_generator import generate_blood_bank_pdf
from app import db
from datetime import datetime
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__)

@reports_bp.before_request
@login_required
def restrict_to_admin():
    """
    Ensure only admin users access reports and PDF exports.
    """
    if current_user.role != 'admin':
        abort(403)

@reports_bp.route('/')
def index():
    """
    Renders reports visual graphs dashboard.
    """
    return render_template('admin/reports.html')

@reports_bp.route('/pdf')
def download_pdf():
    """
    Generates and returns the PDF inventory document.
    """
    buffer = generate_blood_bank_pdf()
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"BloodBank_Report_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    )

@reports_bp.route('/api/data')
def api_data():
    """
    Returns data arrays for 4 charts:
    - Current Blood Stock
    - Donor Blood Group Distribution
    - Blood Request Status Breakdown
    - Monthly Request Demand Trend
    """
    # 1. Current Stock Levels
    stocks = BloodStock.query.order_by(BloodStock.blood_group).all()
    stock_labels = [s.blood_group for s in stocks]
    stock_values = [s.units for s in stocks]
    
    # 2. Donors Distribution
    donor_counts = db.session.query(
        Donor.blood_group, func.count(Donor.id)
    ).group_by(Donor.blood_group).all()
    donor_dist = {group: count for group, count in donor_counts}
    all_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    donor_labels = all_groups
    donor_values = [donor_dist.get(g, 0) for g in all_groups]
    
    # 3. Request Statuses
    status_counts = db.session.query(
        BloodRequest.status, func.count(BloodRequest.id)
    ).group_by(BloodRequest.status).all()
    status_dist = {status: count for status, count in status_counts}
    # Ensure standard statuses exist in labels if not yet stored
    status_labels = list(status_dist.keys()) if status_dist else ['Pending', 'Approved', 'Rejected']
    status_values = [status_dist.get(s, 0) for s in status_labels]
    
    # 4. Monthly Trend (last 6 months)
    requests = BloodRequest.query.order_by(BloodRequest.created_at.asc()).all()
    monthly_trend = {}
    for r in requests:
        month_str = r.created_at.strftime('%Y-%m')
        monthly_trend[month_str] = monthly_trend.get(month_str, 0) + r.quantity
        
    trend_sorted_keys = sorted(monthly_trend.keys())
    if not trend_sorted_keys:
        trend_sorted_keys = [datetime.utcnow().strftime('%Y-%m')]
        monthly_trend = {trend_sorted_keys[0]: 0}
        
    trend_labels = trend_sorted_keys
    trend_values = [monthly_trend[k] for k in trend_sorted_keys]
    
    return jsonify({
        'stock': {
            'labels': stock_labels,
            'values': stock_values
        },
        'donors': {
            'labels': donor_labels,
            'values': donor_values
        },
        'requests': {
            'labels': status_labels,
            'values': status_values
        },
        'trend': {
            'labels': trend_labels,
            'values': trend_values
        }
    })
