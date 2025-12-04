"""Summary and analytics service."""
from datetime import datetime, timedelta
from collections import defaultdict
from app.models import RitualLogEntry, Ritual
from sqlalchemy import func


def get_week_date_range():
    """Get start and end dates for current week (Monday to Sunday)."""
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def calculate_daily_counts(user_id):
    """Calculate ritual counts for each day of the current week."""
    week_start, week_end = get_week_date_range()
    
    entries = RitualLogEntry.query.filter(
        RitualLogEntry.user_id == user_id,
        func.date(RitualLogEntry.created_at) >= week_start,
        func.date(RitualLogEntry.created_at) <= week_end
    ).all()
    
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    daily_counts = {day: 0 for day in day_names}
    
    for entry in entries:
        entry_date = entry.created_at.date()
        day_index = (entry_date - week_start).days
        if 0 <= day_index <= 6:
            daily_counts[day_names[day_index]] += 1
    
    return daily_counts


def calculate_virtue_metrics(user_id):
    """Calculate virtue scores for current week. Primary +1, Secondary +0.5."""
    week_start, week_end = get_week_date_range()
    
    entries = RitualLogEntry.query.filter(
        RitualLogEntry.user_id == user_id,
        func.date(RitualLogEntry.created_at) >= week_start,
        func.date(RitualLogEntry.created_at) <= week_end
    ).all()
    
    # Initialize all virtues to 0 first to ensure consistent order
    virtue_scores = {'Ren': 0.0, 'Yi': 0.0, 'Li': 0.0, 'Zhi': 0.0}
    
    for entry in entries:
        if entry.ritual:
            if entry.ritual.primary_category:
                virtue_scores[entry.ritual.primary_category] += 1.0
            if entry.ritual.secondary_category:
                virtue_scores[entry.ritual.secondary_category] += 0.5
    
    return virtue_scores


def calculate_all_time_virtue_metrics(user_id):
    """Calculate all-time virtue cultivation scores."""
    entries = RitualLogEntry.query.filter_by(user_id=user_id).all()
    
    # Initialize all virtues to 0 first to ensure consistent order
    virtue_scores = {'Ren': 0.0, 'Yi': 0.0, 'Li': 0.0, 'Zhi': 0.0}
    
    for entry in entries:
        if entry.ritual:
            if entry.ritual.primary_category:
                virtue_scores[entry.ritual.primary_category] += 1.0
            if entry.ritual.secondary_category:
                virtue_scores[entry.ritual.secondary_category] += 0.5
    
    return virtue_scores


def get_total_rituals_this_week(user_id):
    """Get total ritual log entries for current week."""
    week_start, week_end = get_week_date_range()
    return RitualLogEntry.query.filter(
        RitualLogEntry.user_id == user_id,
        func.date(RitualLogEntry.created_at) >= week_start,
        func.date(RitualLogEntry.created_at) <= week_end
    ).count()


def get_total_rituals_last_week(user_id):
    """Get total ritual log entries for last week."""
    week_start, _ = get_week_date_range()
    last_week_start = week_start - timedelta(days=7)
    last_week_end = week_start - timedelta(days=1)
    
    return RitualLogEntry.query.filter(
        RitualLogEntry.user_id == user_id,
        func.date(RitualLogEntry.created_at) >= last_week_start,
        func.date(RitualLogEntry.created_at) <= last_week_end
    ).count()


def get_days_practiced_this_week(user_id):
    """Get number of unique days with ritual logs this week (0-7)."""
    week_start, week_end = get_week_date_range()
    
    results = RitualLogEntry.query.filter(
        RitualLogEntry.user_id == user_id,
        func.date(RitualLogEntry.created_at) >= week_start,
        func.date(RitualLogEntry.created_at) <= week_end
    ).with_entities(func.date(RitualLogEntry.created_at).distinct()).all()
    
    return len(results)


def get_all_time_stats(user_id):
    """Get all-time statistics for a user."""
    from app.models import User, Reflection
    
    total_logs = RitualLogEntry.query.filter_by(user_id=user_id).count()
    total_reflections = Reflection.query.filter_by(user_id=user_id).count()
    
    user = User.query.get(user_id)
    days_on_journey = max(1, (datetime.now() - user.created_at).days + 1) if user else 0
    
    most_practiced = None
    if total_logs > 0:
        result = RitualLogEntry.query.filter_by(user_id=user_id)\
            .join(Ritual)\
            .with_entities(Ritual.name, func.count(RitualLogEntry.id).label('count'))\
            .group_by(Ritual.name)\
            .order_by(func.count(RitualLogEntry.id).desc())\
            .first()
        if result:
            most_practiced = {'name': result[0], 'count': result[1]}
    
    return {
        'total_logs': total_logs,
        'total_reflections': total_reflections,
        'days_on_journey': days_on_journey,
        'most_practiced': most_practiced,
        'longest_streak': calculate_longest_streak(user_id),
        'virtue_metrics': calculate_all_time_virtue_metrics(user_id)
    }


def get_weekly_trend(user_id, weeks=8):
    """Get ritual counts for the last N weeks."""
    today = datetime.now().date()
    current_week_start = today - timedelta(days=today.weekday())
    
    weekly_data = []
    for i in range(weeks - 1, -1, -1):
        week_start = current_week_start - timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        
        count = RitualLogEntry.query.filter(
            RitualLogEntry.user_id == user_id,
            func.date(RitualLogEntry.created_at) >= week_start,
            func.date(RitualLogEntry.created_at) <= week_end
        ).count()
        
        label = week_start.strftime('%b %d')
        weekly_data.append({'label': label, 'count': count})
    
    return weekly_data


def calculate_longest_streak(user_id):
    """Calculate longest streak of consecutive days with ritual logs."""
    results = RitualLogEntry.query.filter_by(user_id=user_id)\
        .with_entities(func.date(RitualLogEntry.created_at).distinct())\
        .order_by(func.date(RitualLogEntry.created_at))\
        .all()
    
    if not results:
        return 0
    
    # Convert to date objects (SQLite returns strings)
    dates = []
    for r in results:
        d = r[0]
        if isinstance(d, str):
            d = datetime.strptime(d, '%Y-%m-%d').date()
        elif isinstance(d, datetime):
            d = d.date()
        dates.append(d)
    
    dates = sorted(dates)
    if not dates:
        return 0
    
    longest = 1
    current = 1
    
    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days == 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    
    return longest


def calculate_current_streak(user_id):
    """Calculate current streak of consecutive days with ritual logs."""
    today = datetime.now().date()
    streak = 0
    
    for i in range(365):
        check_date = today - timedelta(days=i)
        has_log = RitualLogEntry.query.filter(
            RitualLogEntry.user_id == user_id,
            func.date(RitualLogEntry.created_at) == check_date
        ).first()
        
        if has_log:
            streak += 1
        else:
            if i == 0:
                continue
            break
    
    return streak
