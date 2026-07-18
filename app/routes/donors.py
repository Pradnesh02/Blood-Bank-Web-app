from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.donor import Donor
from datetime import datetime
from app.ml.eligibility import predict_donor_eligibility

donors_bp = Blueprint('donors', __name__)

@donors_bp.before_request
@login_required
def restrict_to_admin():
    """
    Ensure only admin users access donor management.
    """
    if current_user.role != 'admin':
        abort(403)

@donors_bp.route('/')
def index():
    """
    Lists donors, optionally filtering by blood group or searching by string.
    Injects donor eligibility evaluations via ML.
    """
    blood_group_filter = request.args.get('blood_group')
    search_query = request.args.get('search')
    
    query = Donor.query
    
    if blood_group_filter and blood_group_filter != 'All':
        query = query.filter_by(blood_group=blood_group_filter)
        
    if search_query:
        query = query.filter(
            (Donor.name.ilike(f"%{search_query}%")) | 
            (Donor.phone.ilike(f"%{search_query}%")) |
            (Donor.address.ilike(f"%{search_query}%"))
        )
        
    donors = query.order_by(Donor.name).all()
    
    # Calculate eligibility for each donor to show directly in the table
    donor_eligibility = {}
    for d in donors:
        donor_eligibility[d.id] = predict_donor_eligibility(d)
        
    return render_template(
        'admin/donors.html', 
        donors=donors, 
        selected_group=blood_group_filter or 'All',
        search_query=search_query or '',
        donor_eligibility=donor_eligibility
    )

@donors_bp.route('/add', methods=['GET', 'POST'])
def add():
    """
    Renders add form or inserts a new donor record.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        age_str = request.form.get('age')
        phone = request.form.get('phone')
        address = request.form.get('address')
        blood_group = request.form.get('blood_group')
        last_donation_str = request.form.get('last_donation_date')
        health_status = request.form.get('health_status', 'Fit')
        notes = request.form.get('notes')
        
        try:
            age = int(age_str)
            last_donation_date = datetime.strptime(last_donation_str, '%Y-%m-%d').date()
        except (ValueError, TypeError) as e:
            flash('Invalid form input values. Please review and try again.', 'danger')
            return redirect(url_for('donors.add'))
            
        donor = Donor(
            name=name,
            age=age,
            phone=phone,
            address=address,
            blood_group=blood_group,
            last_donation_date=last_donation_date,
            health_status=health_status,
            notes=notes
        )
        db.session.add(donor)
        db.session.commit()
        
        flash('Donor added successfully!', 'success')
        return redirect(url_for('donors.index'))
        
    return render_template('admin/add_donor.html')

@donors_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """
    Renders update form pre-filled or updates the donor in the database.
    """
    donor = Donor.query.get_or_404(id)
    if request.method == 'POST':
        donor.name = request.form.get('name')
        age_str = request.form.get('age')
        donor.phone = request.form.get('phone')
        donor.address = request.form.get('address')
        donor.blood_group = request.form.get('blood_group')
        last_donation_str = request.form.get('last_donation_date')
        donor.health_status = request.form.get('health_status')
        donor.notes = request.form.get('notes')
        
        try:
            donor.age = int(age_str)
            donor.last_donation_date = datetime.strptime(last_donation_str, '%Y-%m-%d').date()
        except (ValueError, TypeError) as e:
            flash('Invalid age or donation date format.', 'danger')
            return redirect(url_for('donors.edit', id=id))
            
        db.session.commit()
        flash('Donor updated successfully!', 'success')
        return redirect(url_for('donors.index'))
        
    return render_template('admin/edit_donor.html', donor=donor)

@donors_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """
    Removes a donor record.
    """
    donor = Donor.query.get_or_404(id)
    db.session.delete(donor)
    db.session.commit()
    flash('Donor deleted successfully.', 'success')
    return redirect(url_for('donors.index'))
