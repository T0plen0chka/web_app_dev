import pytest
from models import db, User, Role

def test_index_page_shows_users(client):
    """1. Проверка отображения списка пользователей на главной странице"""
    response = client.get('/')
    assert response.status_code == 200
    # Проверяем наличие таблицы с пользователями
    assert 'Список пользователей' in response.get_data(as_text=True)

def test_create_user_form_requires_auth(client):
    """2. Проверка доступа к форме создания пользователя (требуется аутентификация)"""
    response = client.get('/user/create/')
    assert response.status_code == 302  # Редирект на страницу входа
    assert '/login/' in response.headers.get('Location', '')

def test_create_user_success(auth_client):
    """3. Проверка успешного создания пользователя"""
    response = auth_client.post('/user/create/', data={
        'username': 'newuser123',
        'password': 'TestPass123!',
        'last_name': 'Иванов',
        'first_name': 'Иван',
        'patronymic': 'Иванович',
        'role_id': 2
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert 'Пользователь успешно создан' in response.get_data(as_text=True)
    
    # Проверка в БД
    user = User.query.filter_by(username='newuser123').first()
    assert user is not None
    assert user.last_name == 'Иванов'

def test_create_user_invalid_username(auth_client):
    """4. Проверка валидации логина (должен быть не менее 5 символов)"""
    response = auth_client.post('/user/create/', data={
        'username': 'usr',  # Слишком короткий
        'password': 'TestPass123!',
        'last_name': 'Иванов',
        'first_name': 'Иван',
        'patronymic': '',
        'role_id': 2
    })
    
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert 'Логин должен содержать не менее 5 символов' in content

def test_create_user_invalid_password(auth_client):
    """5. Проверка валидации пароля (должен быть не менее 8 символов)"""
    response = auth_client.post('/user/create/', data={
        'username': 'validuser',
        'password': 'weak',  # Слишком короткий
        'last_name': 'Иванов',
        'first_name': 'Иван',
        'patronymic': '',
        'role_id': 2
    })
    
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert 'Пароль должен содержать не менее 8 символов' in content

def test_create_user_duplicate_username(auth_client):
    """6. Проверка создания пользователя с существующим логином"""
    # Создаём первого пользователя
    auth_client.post('/user/create/', data={
        'username': 'duplicate',
        'password': 'TestPass123!',
        'last_name': 'Первый',
        'first_name': 'Пользователь',
        'patronymic': '',
        'role_id': 2
    })
    
    # Пытаемся создать второго с таким же логином
    response = auth_client.post('/user/create/', data={
        'username': 'duplicate',
        'password': 'TestPass123!',
        'last_name': 'Второй',
        'first_name': 'Пользователь',
        'patronymic': '',
        'role_id': 2
    })
    
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert 'Пользователь с таким логином уже существует' in content

def test_view_user_page(client):
    """7. Проверка страницы просмотра пользователя (доступна всем)"""
    # Сначала создаём пользователя через аутентифицированного клиента
    # Используем существующего пользователя из фикстуры
    response = client.get('/user/1/')
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert 'Просмотр пользователя' in content

def test_edit_user_form_requires_auth(client):
    """8. Проверка доступа к форме редактирования (требуется аутентификация)"""
    response = client.get('/user/1/edit/')
    assert response.status_code == 302
    assert '/login/' in response.headers.get('Location', '')

def test_edit_user_success(auth_client):
    """9. Проверка успешного редактирования пользователя"""
    response = auth_client.post('/user/1/edit/', data={
        'last_name': 'Петров',
        'first_name': 'Петр',
        'patronymic': 'Петрович',
        'role_id': 2
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert 'Пользователь успешно обновлён' in response.get_data(as_text=True)
    
    # Проверка в БД
    user = User.query.get(1)
    assert user.last_name == 'Петров'
    assert user.first_name == 'Петр'

def test_delete_user_requires_auth(client):
    """10. Проверка доступа к удалению пользователя (требуется аутентификация)"""
    response = client.post('/user/1/delete/')
    assert response.status_code == 302
    assert '/login/' in response.headers.get('Location', '')

def test_delete_user_success(auth_client):
    """11. Проверка успешного удаления пользователя"""
    # Создаём пользователя для удаления
    auth_client.post('/user/create/', data={
        'username': 'todelete',
        'password': 'TestPass123!',
        'last_name': 'Delete',
        'first_name': 'User',
        'patronymic': '',
        'role_id': 2
    })
    
    user_to_delete = User.query.filter_by(username='todelete').first()
    assert user_to_delete is not None
    
    response = auth_client.post(f'/user/{user_to_delete.id}/delete/', follow_redirects=True)
    assert response.status_code == 200
    assert 'Пользователь успешно удалён' in response.get_data(as_text=True)
    
    # Проверка, что пользователь удалён
    deleted_user = User.query.filter_by(username='todelete').first()
    assert deleted_user is None

def test_cannot_delete_self(auth_client):
    """12. Проверка невозможности удаления собственной учётной записи"""
    response = auth_client.post('/user/1/delete/', follow_redirects=True)
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert 'Вы не можете удалить свою собственную учётную запись' in content

def test_change_password_form_requires_auth(client):
    """13. Проверка доступа к форме смены пароля (требуется аутентификация)"""
    response = client.get('/change-password/')
    assert response.status_code == 302
    assert '/login/' in response.headers.get('Location', '')

def test_change_password_success(auth_client):
    """14. Проверка успешной смены пароля"""
    response = auth_client.post('/change-password/', data={
        'old_password': 'Test123!',
        'new_password': 'NewPass456!',
        'confirm_password': 'NewPass456!'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert 'Пароль успешно изменён' in content

def test_change_password_wrong_old(auth_client):
    """15. Проверка смены пароля с неверным старым паролем"""
    response = auth_client.post('/change-password/', data={
        'old_password': 'WrongPassword',
        'new_password': 'NewPass456!',
        'confirm_password': 'NewPass456!'
    })
    
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert 'Неверный текущий пароль' in content

def test_change_password_mismatch(auth_client):
    """16. Проверка смены пароля с несовпадающими новыми паролями"""
    response = auth_client.post('/change-password/', data={
        'old_password': 'Test123!',
        'new_password': 'NewPass456!',
        'confirm_password': 'DifferentPass789!'
    })
    
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert 'Пароли не совпадают' in content

def test_login_success(client):
    """17. Проверка успешной аутентификации"""
    response = client.post('/login/', data={
        'username': 'testuser',
        'password': 'Test123!'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert 'Вы успешно вошли в систему' in content

def test_login_failure(client):
    """18. Проверка неудачной аутентификации"""
    response = client.post('/login/', data={
        'username': 'testuser',
        'password': 'WrongPassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert 'Неверное имя пользователя или пароль' in content

def test_logout(auth_client):
    """19. Проверка выхода из системы"""
    response = auth_client.get('/logout/', follow_redirects=True)
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert 'Вы вышли из системы' in content

def test_empty_fields_validation(auth_client):
    """20. Проверка валидации пустых полей"""
    response = auth_client.post('/user/create/', data={
        'username': '',
        'password': '',
        'last_name': '',
        'first_name': '',
        'patronymic': '',
        'role_id': 2
    })
    
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert 'Логин не может быть пустым' in content
    assert 'Пароль не может быть пустым' in content
    assert 'Фамилия не может быть пустой' in content
    assert 'Имя не может быть пустым' in content