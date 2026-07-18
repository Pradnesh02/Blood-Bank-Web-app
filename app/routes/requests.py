from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app import db
from app.models.request import BloodRequest
from app.models.blood_stock import BloodStock
from app.models.donor import Donor
from datetime import datetime
from app.utils.email_alerts import send_critical_stock_email, send_low_stock_email
from app.ml.compatibility import get_compatible_alternatives

requests_bp = Blueprint('requests', __name__)

@requests_bp.route('/user')
@login_required
def user_requests():
    """
    Renders the request history for the logged-in user.
    """
    requests_list = BloodRequest.query.filter_by(user_id=current_user.id).order_by(BloodRequest.id.desc()).all()
    return render_template('user/my_requests.html', requests=requests_list)

@requests_bp.route('/submit', methods=['POST'])
@login_required
def submit():
    """
    Creates a new blood request submitted by a user.
    """
    blood_group = request.form.get('blood_group')
    quantity_str = request.form.get('quantity')
    hospital_name = request.form.get('hospital_name')
    urgency = request.form.get('urgency', 'Normal')
    required_date_str = request.form.get('required_date')
    notes = request.form.get('notes')
    
    try:
        quantity = int(quantity_str)
        if not (1 <= quantity <= 10):
            raise ValueError()
        required_date = datetime.strptime(required_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        flash('Invalid request parameters. Please verify date and quantity.', 'danger')
        return redirect(url_for('user.request_blood'))
        
    requester_name = request.form.get('requester_name') or current_user.name
    
    blood_request = BloodRequest(
        requester_name=requester_name,
        blood_group=blood_group,
        quantity=quantity,
        hospital_name=hospital_name,
        urgency=urgency,
        required_date=required_date,
        notes=notes,
        status='Pending',
        user_id=current_user.id
    )
    db.session.add(blood_request)
    db.session.commit()
    
    flash('Blood request submitted successfully!', 'success')
    return redirect(url_for('requests.user_requests'))

@requests_bp.route('/admin')
@login_required
def admin_requests():
    """
    Renders all requests in tabs for the administrator.
    """
    if current_user.role != 'admin':
        abort(403)
        
    pending = BloodRequest.query.filter_by(status='Pending').order_by(BloodRequest.id.desc()).all()
    approved = BloodRequest.query.filter_by(status='Approved').order_by(BloodRequest.id.desc()).all()
    rejected = BloodRequest.query.filter_by(status='Rejected').order_by(BloodRequest.id.desc()).all()
    
    return render_template('admin/requests.html', pending=pending, approved=approved, rejected=rejected)

@requests_bp.route('/<int:id>/approve', methods=['POST'])
@login_required
def approve_request(id):
    """
    Approves a blood request, checks stock levels, performs deduction,
    and sends email alerts if stock dips below safety thresholds.
    """
    if current_user.role != 'admin':
        abort(403)
        
    request_obj = BloodRequest.query.get_or_404(id)
    stock = BloodStock.query.filter_by(blood_group=request_obj.blood_group).first()
    
    if not stock:
        return jsonify({'status': 'error', 'message': f'Blood group {request_obj.blood_group} not initialized.'}), 404
        
    # Check sufficient stock
    if stock.units < request_obj.quantity:
        shortage = request_obj.quantity - stock.units
        # Get compatible alternatives and contact donors
        comp_data = get_compatible_alternatives(request_obj.blood_group, request_obj.quantity)
        
        return jsonify({
            'status': 'insufficient',
            'available': stock.units,
            'requested': request_obj.quantity,
            'shortage': shortage,
            'alternatives': comp_data['alternatives'],
            'donors': comp_data['contact_donors']
        }), 400

    # Deduct stock
    stock.units -= request_obj.quantity
    stock.last_updated = datetime.utcnow()
    request_obj.status = 'Approved'
    db.session.commit()

    # Send email alerts asynchronously if configured, otherwise falls back to logging
    try:
        if stock.units == 0:
            send_critical_stock_email(request_obj.blood_group)
        elif stock.units < 5:
            send_low_stock_email(request_obj.blood_group, stock.units)
    except Exception as e:
        # Prevent email failure from breaking the response
        pass

    return jsonify({
        'status': 'approved',
        'remaining': stock.units
    })

@requests_bp.route('/<int:id>/reject', methods=['POST'])
@login_required
def reject_request(id):
    """
    Rejects a blood request with a specific reason.
    """
    if current_user.role != 'admin':
        abort(403)
        
    # Extract JSON or form data
    data = request.get_json() or {}
    reason = data.get('reason') or request.form.get('reason') or 'Not specified'
    
    request_obj = BloodRequest.query.get_or_404(id)
    request_obj.status = 'Rejected'
    request_obj.notes = f"{request_obj.notes or ''} [Rejected Reason: {reason}]".strip()
    db.session.commit()
    
    return jsonify({'status': 'rejected'})

@requests_bp.route('/api/check-stock')
@login_required
def check_stock():
    """
    AJAX endpoint checking current available units for requested group.
    """
    blood_group = request.args.get('blood_group')
    quantity_str = request.args.get('quantity')
    
    try:
        quantity = int(quantity_str)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid quantity.'}), 400
        
    stock = BloodStock.query.filter_by(blood_group=blood_group).first()
    available = stock.units if stock else 0
    
    if available >= quantity:
        return jsonify({'status': 'available', 'available': available})
    else:
        return jsonify({'status': 'insufficient', 'available': available})
