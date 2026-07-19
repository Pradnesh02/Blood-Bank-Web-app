from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.campaign import Campaign
from datetime import datetime, date

campaigns_bp = Blueprint('campaigns', __name__)

# ── Public: View all upcoming campaigns ────────────────
@campaigns_bp.route('/', methods=['GET'])
def list_all():
    """
    Shows notice board of upcoming campaigns.
    Accessible to all users (no login required).
    """
    today = date.today()
    upcoming = Campaign.query.filter(
        Campaign.campaign_date >= today,
        Campaign.is_active == True
    ).order_by(Campaign.campaign_date.asc()).all()

    past = Campaign.query.filter(
        Campaign.campaign_date < today
    ).order_by(Campaign.campaign_date.desc()).limit(5).all()

    # Next campaign (soonest upcoming)
    next_campaign = upcoming[0] if upcoming else None

    return render_template(
        'campaigns/notice_board.html',
        upcoming=upcoming,
        past=past,
        next_campaign=next_campaign,
        today=today
    )

# ── ADMIN: Add new campaign ────────────────────────────
@campaigns_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if current_user.role != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('campaigns.list_all'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        location = request.form.get('location', '').strip()
        address = request.form.get('address', '').strip()
        campaign_date_str = request.form.get('campaign_date')
        campaign_time = request.form.get('campaign_time', '').strip()
        description = request.form.get('description', '').strip()
        target_blood_groups = request.form.get('target_blood_groups', '').strip()
        target_donors = request.form.get('target_donors', type=int)
        organizer_name = request.form.get('organizer_name', '').strip()
        organizer_phone = request.form.get('organizer_phone', '').strip()

        # Validation
        errors = []
        if not title:
            errors.append('Campaign title is required.')
        if not location:
            errors.append('Location is required.')
        if not campaign_date_str:
            errors.append('Campaign date is required.')
        else:
            try:
                campaign_date = datetime.strptime(campaign_date_str, '%Y-%m-%d').date()
                if campaign_date < date.today():
                    errors.append('Campaign date must be in the future.')
            except (ValueError, TypeError):
                errors.append('Invalid date format.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('campaigns/add.html')

        campaign = Campaign(
            title=title,
            location=location,
            address=address,
            campaign_date=campaign_date,
            campaign_time=campaign_time,
            description=description,
            target_blood_groups=target_blood_groups,
            target_donors=target_donors,
            organizer_name=organizer_name,
            organizer_phone=organizer_phone,
            is_active=True
        )

        db.session.add(campaign)
        db.session.commit()

        flash(f'Campaign "{title}" at {location} added successfully!', 'success')
        return redirect(url_for('campaigns.list_all'))

    return render_template('campaigns/add.html')

# ── ADMIN: Delete / deactivate campaign ───────────────
@campaigns_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    campaign = Campaign.query.get_or_404(id)
    campaign.is_active = False
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Campaign removed from notice board.'
    })

# ── API: Next campaign for dashboard widget ────────────
@campaigns_bp.route('/api/next', methods=['GET'])
def next_campaign():
    today = date.today()
    campaign = Campaign.query.filter(
        Campaign.campaign_date >= today,
        Campaign.is_active == True
    ).order_by(Campaign.campaign_date.asc()).first()

    if not campaign:
        return jsonify({'campaign': None})

    days_away = (campaign.campaign_date - today).days

    return jsonify({
        'campaign': {
            'id': campaign.id,
            'title': campaign.title,
            'location': campaign.location,
            'address': campaign.address,
            'date': campaign.campaign_date.strftime('%d %B %Y'),
            'time': campaign.campaign_time,
            'days_away': days_away,
            'target_blood_groups': campaign.target_blood_groups,
            'organizer_name': campaign.organizer_name,
            'organizer_phone': campaign.organizer_phone
        }
    })
