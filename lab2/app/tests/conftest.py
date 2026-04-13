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
def captured_templates(app):
    """Фикстура для захвата шаблонов"""
    from flask import template_rendered
    from contextlib import contextmanager
    
    @contextmanager
    def captured():
        recorded = []
        def record(sender, template, context, **extra):
            recorded.append((template, context))
        template_rendered.connect(record, app)
        try:
            yield recorded
        finally:
            template_rendered.disconnect(record, app)
    
    return captured()

@pytest.fixture
def posts_list():
    """Фикстура с тестовыми постами"""
    from datetime import datetime
    return [
        {
            'title': 'Заголовок поста',
            'text': 'Текст поста для тестирования',
            'author': 'Иванов Иван Иванович',
            'date': datetime(2025, 3, 10),
            'image_id': '123.jpg',
            'comments': []
        }
    ]