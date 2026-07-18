from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app import db
from app.models.blood_stock import BloodStock
from datetime import datetime

stock_bp = Blueprint('stock', __name__)

@stock_bp.before_request
@login_required
def restrict_to_admin():
    """
    Ensure only admin users access inventory controls.
    """
    if current_user.role != 'admin':
        abort(403)

@stock_bp.route('/')
def index():
    """
    Renders the blood inventory grid view.
    """
    stock_levels = BloodStock.query.order_by(BloodStock.blood_group).all()
    return render_template('admin/stock.html', stock_levels=stock_levels)

@stock_bp.route('/update', methods=['POST'])
def update():
    """
    Updates stock levels for a specific blood group.
    """
    blood_group = request.form.get('blood_group')
    units_str = request.form.get('units')
    
    try:
        units = int(units_str)
        if units < 0:
            raise ValueError()
    except (ValueError, TypeError):
        flash('Invalid unit count. Must be a non-negative integer.', 'danger')
        return redirect(url_for('stock.index'))
        
    stock = BloodStock.query.filter_by(blood_group=blood_group).first()
    if stock:
        stock.units = units
        stock.last_updated = datetime.utcnow()
        db.session.commit()
        flash(f'Stock updated successfully: {blood_group} is now {units} units.', 'success')
    else:
        flash(f'Blood group {blood_group} not found.', 'danger')
        
    return redirect(url_for('stock.index'))

@stock_bp.route('/deduct', methods=['POST'])
def deduct():
    """
    API endpoint to deduct units from stock.
    """
    data = request.get_json() or {}
    blood_group = data.get('blood_group')
    try:
        quantity = int(data.get('quantity', 0))
        if quantity <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Quantity must be a positive integer.'}), 400
        
    stock = BloodStock.query.filter_by(blood_group=blood_group).first()
    if not stock:
        return jsonify({'status': 'not_found', 'message': f'Blood group {blood_group} not found.'}), 404
        
    if stock.units < quantity:
        return jsonify({'status': 'insufficient', 'available': stock.units}), 400
        
    stock.units -= quantity
    stock.last_updated = datetime.utcnow()
    db.session.commit()
    return jsonify({'status': 'success', 'remaining': stock.units})

@stock_bp.route('/api/levels')
def levels():
    """
    Returns inventory units for all groups in JSON format.
    """
    stocks = BloodStock.query.order_by(BloodStock.blood_group).all()
    return jsonify({s.blood_group: s.units for s in stocks})
