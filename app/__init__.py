"""Flask application factory."""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Database: use PostgreSQL if DATABASE_URL exists, otherwise SQLite
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Render uses postgres:// but SQLAlchemy needs postgresql+psycopg://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql+psycopg://', 1)
        elif database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rituals.db'
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Register routes and create tables
    with app.app_context():
        from app.routes import register_routes
        register_routes(app)
        
        db.create_all()
        
        # Initialize preset rituals if empty
        from app.models import Ritual
        if Ritual.query.filter_by(user_id=None).count() == 0:
            _initialize_preset_rituals()
    
    return app


def _initialize_preset_rituals():
    """Initialize shared preset rituals."""
    from app.models import Ritual
    
    presets = [
        (
            'Morning Filial Check-In',
            'Each morning, intentionally check in with a parent or elder about their day, listening with full attention rather than multitasking.',
            'Ren', 'Li', 'Analects 1.6; 2.7'
        ),
        (
            'Respectful Greeting to Elders or Teachers',
            'When meeting an elder or teacher, stand if seated, offer a deliberate greeting, and give undivided attention for the first moments of interaction.',
            'Li', 'Ren', 'Analects 1.6; 10.3-10.5'
        ),
        (
            'Three-Breath Speech Pause',
            'Before responding in a charged moment, pause for three breaths to sense the standpoint of other people and choose words that are respectful and precise.',
            'Zhi', 'Yi', 'Analects 1.4; 4.24'
        ),
        (
            'Daily Three-Point Self-Examination',
            'At the end of the day, review whether you were trustworthy, followed through on what you advised, and practiced what you are learning.',
            'Zhi', 'Yi', 'Analects 1.4 (Zengzi\'s three examinations)'
        ),
        (
            'Study-and-Practice Mini Session',
            'Study a brief passage or idea and then design one small concrete action to practice it before the day ends.',
            'Zhi', 'Li', 'Analects 1.1'
        ),
        (
            'Small Daily Act of Ren',
            'Seek out one concrete act of kindness—especially where you would normally stay on autopilot—and carry it through to completion.',
            'Ren', 'Zhi', 'Analects 4.3; 12.22'
        ),
        (
            'Conquer-the-Self Pause',
            'When anger or resentment surges, notice the familiar pattern, suspend your first impulse, and submit to a chosen ritual response instead.',
            'Yi', 'Li', 'Analects 12.1 ("conquer the self and submit to ritual")'
        ),
        (
            'Courteous Greeting Ritual',
            'In everyday greetings, pay attention to posture, tone, and eye contact, treating even brief encounters as mini-rituals of respect.',
            'Li', 'Ren', 'Analects 10.1-10.9'
        ),
    ]
    
    for name, desc, primary, secondary, source in presets:
        db.session.add(Ritual(
            name=name, description=desc,
            primary_category=primary, secondary_category=secondary,
            source=source, user_id=None
        ))
    
    db.session.commit()
