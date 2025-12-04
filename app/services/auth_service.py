"""Authentication service."""
from app import db
from app.models import User


def validate_registration_data(username, password, password_confirm):
    """Validate registration form data. Returns list of errors."""
    errors = []
    
    if not username or not password:
        errors.append('Username and password are required.')
        return errors
    
    if len(username) < 3:
        errors.append('Username must be at least 3 characters long.')
    
    if len(password) < 6:
        errors.append('Password must be at least 6 characters long.')
    
    if password != password_confirm:
        errors.append('Passwords do not match.')
    
    return errors


def check_user_exists(username):
    """Check if username exists. Returns (exists, error_message)."""
    if User.query.filter_by(username=username).first():
        return True, 'Username already exists. Please choose a different one.'
    return False, None


def create_user(username, password):
    """Create a new user account."""
    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return new_user


def authenticate_user(username, password):
    """Authenticate user. Returns (user, error_message)."""
    if not username or not password:
        return None, 'Username and password are required.'
    
    user = User.query.filter_by(username=username).first()
    
    if user is None or not user.check_password(password):
        return None, 'Invalid username or password.'
    
    return user, None
