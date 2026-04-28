from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))
    
    users = db.relationship('User', backref='role', lazy=True)
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    patronymic = db.Column(db.String(100), default='')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def full_name(self):
        """Возвращает ФИО пользователя"""
        parts = [self.last_name, self.first_name]
        if self.patronymic:
            parts.append(self.patronymic)
        return ' '.join(parts)