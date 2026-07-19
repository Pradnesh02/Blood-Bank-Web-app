from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()

@login_manager.user_loader
def load_user(user_id):
    from .models.user import User
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.user import user_bp
    from .routes.donors import donors_bp
    from .routes.stock import stock_bp
    from .routes.requests import requests_bp
    from .routes.reports import reports_bp
    from .routes.ml import ml_bp
    from .routes.appointments import appointments_bp
    from .routes.campaigns import campaigns_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(donors_bp, url_prefix='/donors')
    app.register_blueprint(stock_bp, url_prefix='/stock')
    app.register_blueprint(requests_bp, url_prefix='/requests')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(ml_bp, url_prefix='/ml')
    app.register_blueprint(appointments_bp, url_prefix='/appointments')
    app.register_blueprint(campaigns_bp, url_prefix='/campaigns')

    # Seed initial database states
    with app.app_context():
        try:
            from app.models import User, Donor, BloodStock, BloodRequest, Appointment, Campaign
            db.create_all()
            seed_blood_stock()
            seed_admin_user()
            from app.utils.helpers import seed_historical_data
            seed_historical_data()
        except Exception as e:
            app.logger.warning(f"Database initialization deferred (database might be offline or setup is pending): {e}")

    @app.route('/')
    def landing():
        from flask_login import current_user
        from flask import redirect, url_for, render_template
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.dashboard'))
            
        from app.models.donor import Donor
        from app.models.blood_stock import BloodStock
        from app.models.request import BloodRequest
        
        total_donors = Donor.query.count()
        total_units = db.session.query(db.func.sum(BloodStock.units)).scalar() or 0
        lives_saved = BloodRequest.query.filter_by(status='Approved').count() * 3
        
        return render_template('landing.html', total_donors=total_donors, total_units=total_units, lives_saved=lives_saved)

    return app

def seed_blood_stock():
    from .models.blood_stock import BloodStock
    blood_groups = ['A+','A-','B+','B-','O+','O-','AB+','AB-']
    for group in blood_groups:
        existing = BloodStock.query.filter_by(blood_group=group).first()
        if not existing:
            stock = BloodStock(blood_group=group, units=0)
            db.session.add(stock)
    db.session.commit()

def seed_admin_user():
    from .models.user import User
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(
            name='System Admin',
            email='admin@bloodbank.com',
            password_hash=hashed_pw,
            role='admin',
            blood_group='O+',
            phone='1234567890'
        )
        db.session.add(admin)
        db.session.commit()
