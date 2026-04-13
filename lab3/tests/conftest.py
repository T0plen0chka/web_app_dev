import sys
import os

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import app as application

@pytest.fixture
def app():
    """Фикстура для создания экземпляра приложения"""
    application.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost.localdomain'
    })
    return application

@pytest.fixture
def client(app):
    """Фикстура для создания тестового клиента"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Фикстура для создания клиента командной строки"""
    return app.test_cli_runner()