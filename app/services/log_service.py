"""Ritual log entry service."""
from datetime import datetime
from app import db
from app.models import RitualLogEntry


def create_log_entry(user_id, ritual_id, context, reflection):
    """Create a new ritual log entry."""
    entry = RitualLogEntry(
        ritual_id=ritual_id,
        context=context,
        reflection=reflection,
        user_id=user_id,
        created_at=datetime.utcnow()
    )
    db.session.add(entry)
    db.session.commit()
    return entry


def get_user_ritual_logs(user_id, limit=None):
    """Get all ritual log entries for a user, most recent first."""
    query = RitualLogEntry.query.filter_by(user_id=user_id)\
                                 .order_by(RitualLogEntry.created_at.desc())
    if limit:
        query = query.limit(limit)
    return query.all()


def get_user_ritual_logs_paginated(user_id, page=1, per_page=10):
    """Get paginated ritual log entries for a user."""
    return RitualLogEntry.query.filter_by(user_id=user_id)\
                               .order_by(RitualLogEntry.created_at.desc())\
                               .paginate(page=page, per_page=per_page, error_out=False)


def get_user_logs_for_period(user_id, start_date, end_date):
    """Get ritual logs for a specific time period."""
    return RitualLogEntry.query.filter(
        RitualLogEntry.user_id == user_id,
        RitualLogEntry.created_at >= start_date,
        RitualLogEntry.created_at < end_date
    ).all()


def get_log_entry_by_id(entry_id):
    """Get a single ritual log entry by ID."""
    return RitualLogEntry.query.get(entry_id)


def update_log_entry(entry, ritual_id, context, reflection):
    """Update an existing ritual log entry."""
    entry.ritual_id = ritual_id
    entry.context = context
    entry.reflection = reflection
    db.session.commit()
    return entry


def delete_log_entry(entry):
    """Delete a ritual log entry."""
    db.session.delete(entry)
    db.session.commit()
    return True


def can_user_modify_log(entry, user_id):
    """Check if user owns this log entry."""
    return entry.user_id == user_id
