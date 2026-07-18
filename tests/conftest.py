import pytest
from app import create_app, db

class TestingConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    ADMIN_EMAIL = 'admin@bloodbank.com'

@pytest.fixture
def app():
    """
    Creates an isolated Flask application instance with an in-memory SQLite database
    configured specifically for unit testing.
    """
    app_instance = create_app(TestingConfig)
    
    with app_instance.app_context():
        db.create_all()
        yield app_instance
        db.drop_all()

@pytest.fixture
def client(app):
    """
    Returns a Flask test client.
    """
    return app.test_client()
