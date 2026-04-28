import pytest
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(__file__))

from app import app as application
from models import db, User, Role
from werkzeug.security import generate_password_hash
from datetime import datetime

@pytest.fixture
def app():
    """Фикстура для создания экземпляра приложения"""
    application.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost.localdomain'
    })
    
    with application.app_context():
        db.create_all()
        
        # Создаём тестовые роли
        roles = [
            Role(id=1, name='admin', description='Администратор'),
            Role(id=2, name='user', description='Пользователь')
        ]
        for role in roles:
            if not Role.query.get(role.id):
                db.session.add(role)
        
        # Создаём тестового пользователя
        if not User.query.get(1):
            test_user = User(
                id=1,
                username='testuser',
                password_hash=generate_password_hash('Test123!'),
                last_name='Тестов',
                first_name='Тест',
                patronymic='Тестович',
                role_id=2,
                created_at=datetime.now()
            )
            db.session.add(test_user)
        
        db.session.commit()
    
    yield application
    
    with application.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Фикстура для создания тестового клиента"""
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    """Фикстура для аутентифицированного клиента"""
    # Выполняем логин
    response = client.post('/login/', data={
        'username': 'testuser',
        'password': 'Test123!'
    }, follow_redirects=True)
    
    return client

@pytest.fixture
def runner(app):
    """Фикстура для создания клиента командной строки"""
    return app.test_cli_runner()