"""Reflection journal service."""
from datetime import datetime
from app import db
from app.models import Reflection


def create_reflection(user_id, reflection_text):
    """Create a new reflection entry."""
    reflection = Reflection(
        user_id=user_id,
        reflection_text=reflection_text,
        created_at=datetime.utcnow()
    )
    db.session.add(reflection)
    db.session.commit()
    return reflection


def get_user_reflections(user_id, limit=None):
    """Get all reflections for a user, most recent first."""
    query = Reflection.query.filter_by(user_id=user_id)\
                            .order_by(Reflection.created_at.desc())
    if limit:
        query = query.limit(limit)
    return query.all()


def get_user_reflections_paginated(user_id, page=1, per_page=10):
    """Get paginated reflections for a user."""
    return Reflection.query.filter_by(user_id=user_id)\
                           .order_by(Reflection.created_at.desc())\
                           .paginate(page=page, per_page=per_page, error_out=False)


def get_reflection_count(user_id):
    """Get total number of reflections for a user."""
    return Reflection.query.filter_by(user_id=user_id).count()


def delete_reflection(reflection_id, user_id):
    """Delete a reflection if owned by user. Returns True if deleted."""
    reflection = Reflection.query.filter_by(id=reflection_id, user_id=user_id).first()
    if not reflection:
        return False
    db.session.delete(reflection)
    db.session.commit()
    return True
