from flask_mail import Message
from flask import current_app
from app import mail
from app.models.donor import Donor
import logging

logger = logging.getLogger(__name__)

def send_critical_stock_email(blood_group):
    """
    Emails the admin notifying that stock has reached 0 units,
    supplying list of fit donors for rapid outreach.
    """
    donors = Donor.query.filter_by(blood_group=blood_group, health_status='Fit').all()
    donor_list = '\n'.join([f"- {d.name}: {d.phone}" for d in donors])
    if not donor_list:
        donor_list = "- (No registered active fit donors found)"
        
    admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@bloodbank.com')
    subject = f'🚨 CRITICAL: {blood_group} Blood OUT OF STOCK'
    body = f"""
CRITICAL ALERT — Blood Bank Management System

Blood group {blood_group} has reached ZERO units.

Please contact the following registered donors immediately:
{donor_list}

Login to manage stock: https://bloodbank.onrender.com/admin
"""
    msg = Message(
        subject=subject,
        sender='noreply@bloodbank.com',
        recipients=[admin_email],
        body=body
    )
    
    # Safely send or print email
    try:
        # Check if email is set up
        if current_app.config.get('MAIL_USERNAME') and current_app.config.get('MAIL_USERNAME') != 'admin@bloodbank.com':
            mail.send(msg)
            logger.info(f"Critical stock email sent to {admin_email}")
        else:
            mock_log_email(admin_email, subject, body)
    except Exception as e:
        logger.error(f"Failed to send critical email alert: {str(e)}")
        mock_log_email(admin_email, subject, body)

def send_low_stock_email(blood_group, remaining):
    """
    Emails the admin warning of low stock.
    """
    admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@bloodbank.com')
    subject = f'⚠️ Low Stock Warning: {blood_group} — {remaining} units remaining'
    body = f"""
LOW STOCK ALERT — Blood Bank Management System

Blood group {blood_group} is running LOW.
Remaining: {remaining} unit(s)

Please arrange donations or procure from other sources.
Login: https://bloodbank.onrender.com/admin
"""
    msg = Message(
        subject=subject,
        sender='noreply@bloodbank.com',
        recipients=[admin_email],
        body=body
    )
    
    try:
        if current_app.config.get('MAIL_USERNAME') and current_app.config.get('MAIL_USERNAME') != 'admin@bloodbank.com':
            mail.send(msg)
            logger.info(f"Low stock email sent to {admin_email}")
        else:
            mock_log_email(admin_email, subject, body)
    except Exception as e:
        logger.error(f"Failed to send low stock email: {str(e)}")
        mock_log_email(admin_email, subject, body)

def mock_log_email(recipient, subject, body):
    """
    Helper to print emails to stdout in development mode.
    """
    divider = "★" * 60
    logger.info(f"SMTP not configured or failed. Logged email text to console:")
    print(f"\n{divider}\n[MOCK EMAIL TO: {recipient}]\nSubject: {subject}\n\n{body}\n{divider}\n")
