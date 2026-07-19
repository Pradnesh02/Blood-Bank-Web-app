from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.appointment import Appointment
from app.models.donor import Donor
from app.models.blood_stock import BloodStock
from app.utils.email_alerts import send_appointment_confirmation
from datetime import datetime, date, time

appointments_bp = Blueprint('appointments', __name__)

# ── USER: Book appointment page ────────────────────────
@appointments_bp.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    """
    GET: Show appointment booking form
    POST: Save appointment to DB
    """
    donors = Donor.query.order_by(Donor.name).all()

    if request.method == 'POST':
        donor_id = request.form.get('donor_id')
        appointment_date_str = request.form.get('appointment_date')
        slot = request.form.get('slot')
        notes = request.form.get('notes', '')

        # ── Validation ─────────────────────────────────
        errors = []

        if not donor_id:
            errors.append('Please select a donor.')

        donor = Donor.query.get(donor_id)
        if not donor:
            errors.append('Donor not found.')

        # Weight eligibility check
        if donor and not donor.is_weight_eligible:
            if donor.weight is None:
                errors.append('Donor weight not recorded. Please update donor profile first.')
            else:
                errors.append(f'Donor {donor.name} weighs {donor.weight}kg which is below the minimum 50kg requirement and is NOT eligible to donate.')

        # Date eligibility check
        if donor and not donor.is_date_eligible:
            errors.append(
                f'Donor {donor.name} last donated on {donor.last_donation_date.strftime("%d %b %Y")}. '
                f'Next eligible date: {donor.next_donation_date.strftime("%d %b %Y")} '
                f'({donor.days_until_eligible} days remaining).'
            )

        if not appointment_date_str:
            errors.append('Please select appointment date.')
        else:
            try:
                appt_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
                if appt_date < date.today():
                    errors.append('Appointment date cannot be in the past.')
            except (ValueError, TypeError):
                errors.append('Invalid date format.')

        if not slot:
            errors.append('Please select a time slot.')

        # Check for duplicate appointment on same date
        if donor_id and appointment_date_str and not errors:
            existing = Appointment.query.filter_by(
                donor_id=donor_id,
                appointment_date=appt_date,
                status='Scheduled'
            ).first()
            if existing:
                errors.append('This donor already has a scheduled appointment on that date.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('appointments/book.html', donors=donors)

        # ── Save appointment ────────────────────────────
        appointment = Appointment(
            donor_id=int(donor_id),
            appointment_date=appt_date,
            appointment_time=time(9, 0),  # default
            slot=slot,
            blood_group=donor.blood_group,
            units_to_donate=1,
            notes=notes,
            status='Scheduled'
        )

        db.session.add(appointment)
        db.session.commit()

        # Send confirmation email
        try:
            send_appointment_confirmation(donor, appointment)
        except Exception:
            pass  # Don't crash if email fails

        flash(f'Appointment booked successfully for {donor.name} on {appt_date.strftime("%d %b %Y")} ({slot})!', 'success')
        return redirect(url_for('appointments.list_all'))

    return render_template('appointments/book.html', donors=donors)

# ── ADMIN: View all appointments ────────────────────────
@appointments_bp.route('/', methods=['GET'])
@login_required
def list_all():
    status_filter = request.args.get('status', 'all')

    query = Appointment.query.join(Donor)

    if status_filter != 'all':
        query = query.filter(Appointment.status == status_filter)

    appointments = query.order_by(Appointment.appointment_date.asc()).all()

    counts = {
        'scheduled': Appointment.query.filter_by(status='Scheduled').count(),
        'completed': Appointment.query.filter_by(status='Completed').count(),
        'cancelled': Appointment.query.filter_by(status='Cancelled').count(),
        'no_show': Appointment.query.filter_by(status='No Show').count(),
    }

    return render_template(
        'appointments/list.html',
        appointments=appointments,
        counts=counts,
        status_filter=status_filter
    )

# ── ADMIN: Mark appointment as Completed ──────────────────
@appointments_bp.route('/<int:id>/complete', methods=['POST'])
@login_required
def complete(id):
    """
    When admin marks appointment as Completed:
    1. Update appointment status → Completed
    2. Update donor.last_donation_date → today
    3. Add units to BloodStock for donor's blood group
    4. Send thank-you email to donor
    """
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    appointment = Appointment.query.get_or_404(id)
    donor = appointment.donor

    if appointment.status != 'Scheduled':
        return jsonify({'error': 'Appointment is not in Scheduled status'}), 400

    units = request.form.get('units_donated', 1, type=int)
    if units < 1 or units > 2:
        return jsonify({'error': 'Units donated must be 1 or 2'}), 400

    # ── Step 1: Update appointment ──────────────────────
    appointment.status = 'Completed'
    appointment.units_donated = units
    appointment.stock_updated_at = datetime.utcnow()

    # ── Step 2: Update donor last donation date ─────────
    donor.last_donation_date = date.today()

    # ── Step 3: Update blood stock ──────────────────────
    stock = BloodStock.query.filter_by(blood_group=donor.blood_group).first()

    if stock:
        stock.units += units
        stock.last_updated = datetime.utcnow()
    else:
        # Create stock entry if doesn't exist
        stock = BloodStock(blood_group=donor.blood_group, units=units)
        db.session.add(stock)

    db.session.commit()

    # ── Step 4: Send thank-you email ────────────────────
    try:
        from app.utils.email_alerts import send_donation_thank_you
        send_donation_thank_you(donor, units, donor.next_donation_date)
    except Exception:
        pass

    return jsonify({
        'status': 'success',
        'message': f'Appointment completed! {units} unit(s) of {donor.blood_group} added to stock. New stock: {stock.units} units. {donor.name} next eligible on {donor.next_donation_date.strftime("%d %b %Y")}',
        'new_stock': stock.units,
        'next_donation_date': str(donor.next_donation_date)
    })

# ── ADMIN: Cancel appointment ───────────────────────────
@appointments_bp.route('/<int:id>/cancel', methods=['POST'])
@login_required
def cancel(id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    appointment = Appointment.query.get_or_404(id)
    reason = request.form.get('reason', 'No reason given')

    appointment.status = 'Cancelled'
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': f'Appointment cancelled. Reason: {reason}'
    })

# ── API: Get available slots for a date ─────────────────
@appointments_bp.route('/api/slots', methods=['GET'])
@login_required
def available_slots():
    appt_date = request.args.get('date')
    if not appt_date:
        return jsonify({'slots': []})

    all_slots = [
        'Morning (9AM-12PM)',
        'Afternoon (12PM-3PM)',
        'Evening (3PM-6PM)'
    ]

    # Count appointments per slot for that date
    booked_counts = {}
    for slot in all_slots:
        count = Appointment.query.filter_by(
            appointment_date=appt_date,
            slot=slot,
            status='Scheduled'
        ).count()
        booked_counts[slot] = count

    # Max 20 donors per slot
    MAX_PER_SLOT = 20

    slots_info = []
    for slot in all_slots:
        booked = booked_counts.get(slot, 0)
        available = MAX_PER_SLOT - booked
        slots_info.append({
            'slot': slot,
            'booked': booked,
            'available': available,
            'is_full': available <= 0
        })

    return jsonify({'slots': slots_info})

# ── API: Check donor eligibility before booking ─────────
@appointments_bp.route('/api/check-eligibility', methods=['GET'])
@login_required
def check_eligibility():
    donor_id = request.args.get('donor_id')
    if not donor_id:
        return jsonify({'eligible': False, 'message': 'No donor selected'})

    donor = Donor.query.get(donor_id)
    if not donor:
        return jsonify({'eligible': False, 'message': 'Donor not found'})

    issues = []
    warnings = []

    # Weight check
    if donor.weight is None:
        issues.append('Weight not recorded — please update donor profile')
    elif donor.weight < 50:
        issues.append(f'Weight {donor.weight}kg is below minimum 50kg requirement')

    # Date check
    if not donor.is_date_eligible:
        issues.append(f'Next eligible donation date: {donor.next_donation_date.strftime("%d %b %Y")} ({donor.days_until_eligible} days remaining)')

    # Age check
    if donor.age < 18 or donor.age > 65:
        issues.append(f'Age {donor.age} is outside eligible range (18-65 years)')

    # Health check
    if donor.health_status == 'Unfit':
        issues.append('Donor marked as Unfit — medical clearance required')

    eligible = len(issues) == 0

    return jsonify({
        'eligible': eligible,
        'donor_name': donor.name,
        'blood_group': donor.blood_group,
        'weight': donor.weight,
        'weight_eligible': donor.is_weight_eligible,
        'date_eligible': donor.is_date_eligible,
        'last_donation': str(donor.last_donation_date) if donor.last_donation_date else None,
        'next_donation_date': str(donor.next_donation_date) if donor.next_donation_date else None,
        'days_until_eligible': donor.days_until_eligible,
        'issues': issues,
        'warnings': warnings
    })
