"""Ritual management service."""
from app import db
from app.models import Ritual


def get_available_rituals(user_id):
    """Get all rituals available to a user (presets + custom)."""
    return Ritual.query.filter(
        (Ritual.user_id == None) | (Ritual.user_id == user_id)
    ).order_by(Ritual.user_id.nullsfirst(), Ritual.name).all()


def get_preset_rituals():
    """Get all shared preset rituals."""
    return Ritual.query.filter_by(user_id=None).all()


def get_user_custom_rituals(user_id):
    """Get all custom rituals created by a user."""
    return Ritual.query.filter_by(user_id=user_id).order_by(Ritual.created_at.desc()).all()


def get_ritual_by_id(ritual_id):
    """Get a ritual by ID."""
    return Ritual.query.get(ritual_id)


def create_custom_ritual(user_id, name, description=None, primary_category=None, 
                         secondary_category=None, source=None):
    """Create a new custom ritual for a user."""
    ritual = Ritual(
        name=name,
        description=description or None,
        primary_category=primary_category or None,
        secondary_category=secondary_category or None,
        source=source or None,
        user_id=user_id
    )
    db.session.add(ritual)
    db.session.commit()
    return ritual


def update_custom_ritual(ritual, name, description=None, primary_category=None,
                         secondary_category=None, source=None):
    """Update an existing custom ritual."""
    ritual.name = name
    ritual.description = description or None
    ritual.primary_category = primary_category or None
    ritual.secondary_category = secondary_category or None
    ritual.source = source or None
    db.session.commit()
    return ritual


def delete_custom_ritual(ritual):
    """Delete a custom ritual. Returns False if ritual has been used in logs."""
    if ritual.log_entries:
        return False
    db.session.delete(ritual)
    db.session.commit()
    return True


def can_user_modify_ritual(ritual, user_id):
    """Check if user owns this ritual."""
    return ritual.user_id == user_id
