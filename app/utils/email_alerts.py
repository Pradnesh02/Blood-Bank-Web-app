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

def send_appointment_confirmation(donor, appointment):
    """
    Emails the donor confirming their booked appointment.
    """
    subject = f'📅 Blood Donation Appointment Confirmed: {appointment.appointment_date.strftime("%d %b %Y")}'
    body = f"""
Dear {donor.name},

Your blood donation appointment has been successfully scheduled.

Details:
- Date: {appointment.appointment_date.strftime("%d %b %Y")}
- Slot: {appointment.slot}
- Blood Group: {donor.blood_group}

Thank you for your willingness to save lives!

Best regards,
Blood Bank Team
"""
    admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@bloodbank.com')
    msg = Message(
        subject=subject,
        sender='noreply@bloodbank.com',
        recipients=[admin_email],
        body=body
    )
    
    try:
        if current_app.config.get('MAIL_USERNAME') and current_app.config.get('MAIL_USERNAME') != 'admin@bloodbank.com':
            mail.send(msg)
            logger.info(f"Appointment confirmation email sent for {donor.name}")
        else:
            mock_log_email(admin_email, subject, body)
    except Exception as e:
        logger.error(f"Failed to send appointment confirmation: {str(e)}")
        mock_log_email(admin_email, subject, body)

def send_donation_thank_you(donor, units, next_donation_date):
    """
    Emails a thank you note to the donor with their next eligible date.
    """
    subject = f'🩸 Thank You for Your Blood Donation!'
    body = f"""
Dear {donor.name},

Thank you so much for donating {units} unit(s) of {donor.blood_group} blood today!

Your contribution makes a huge difference in saving lives.

According to medical guidelines, your next eligible donation date is:
- Next eligible date: {next_donation_date.strftime("%d %b %Y")}

We look forward to seeing you again.

Best regards,
Blood Bank Team
"""
    admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@bloodbank.com')
    msg = Message(
        subject=subject,
        sender='noreply@bloodbank.com',
        recipients=[admin_email],
        body=body
    )
    
    try:
        if current_app.config.get('MAIL_USERNAME') and current_app.config.get('MAIL_USERNAME') != 'admin@bloodbank.com':
            mail.send(msg)
            logger.info(f"Thank you email sent for {donor.name}")
        else:
            mock_log_email(admin_email, subject, body)
    except Exception as e:
        logger.error(f"Failed to send thank you email: {str(e)}")
        mock_log_email(admin_email, subject, body)
