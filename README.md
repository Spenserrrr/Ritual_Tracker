# Ritual Tracker

A Flask web app for tracking Confucian ritual practices.

**Deployed on Render:** https://ritual-tracker.onrender.com

Note: This is on Render's free tier, so the first request may be slow (server spins down after inactivity). The database will be inactive after ~30 days (~January 2026).

## Local Setup

```bash
cd Codebase
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run
```

Open http://localhost:5000, register an account, and start logging rituals.

## What it does

- Log daily ritual practices with context and reflection
- Track four Confucian virtues: 仁 Ren, 义 Yi, 礼 Li, 智 Zhi
- 8 preset rituals from the Analects, plus custom rituals you create
- Weekly and all-time statistics
- Reflection journal

## Project Structure

```
app/
├── __init__.py       # Flask app factory
├── models.py         # User, Ritual, RitualLogEntry, Reflection
├── routes.py         # All routes
├── services/         # Business logic
├── templates/        # HTML templates
└── static/           # CSS and JS
wsgi.py               # Entry point
requirements.txt      # Dependencies
Procfile              # For deployment
```

## Deployment

If you want to deploy your own version, you can deploy on Render or Heroku. Set these environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Random secret for sessions

Start command: `gunicorn wsgi:app`
