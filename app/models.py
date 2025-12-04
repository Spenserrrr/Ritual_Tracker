"""Database models."""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    ritual_logs = db.relationship('RitualLogEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    reflections = db.relationship('Reflection', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Ritual(db.Model):
    __tablename__ = 'rituals'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    primary_category = db.Column(db.String(50))
    secondary_category = db.Column(db.String(50), nullable=True)
    source = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    log_entries = db.relationship('RitualLogEntry', backref='ritual', lazy=True)
    owner = db.relationship('User', backref='custom_rituals', lazy=True)
    
    @property
    def is_preset(self):
        return self.user_id is None


class RitualLogEntry(db.Model):
    __tablename__ = 'ritual_log_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    ritual_id = db.Column(db.Integer, db.ForeignKey('rituals.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    context = db.Column(db.String(50))
    reflection = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    @property
    def ritual_name(self):
        return self.ritual.name if self.ritual else "Unnamed Ritual"


class Reflection(db.Model):
    __tablename__ = 'reflections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reflection_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
