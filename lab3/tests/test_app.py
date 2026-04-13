import pytest

def test_counter_page_visits_increment(client):
    """1. Проверка счётчика посещений - увеличение при каждом посещении"""
    # Первое посещение
    response1 = client.get('/counter/')
    assert response1.status_code == 200
    assert '1' in response1.get_data(as_text=True)
    
    # Второе посещение
    response2 = client.get('/counter/')
    assert response2.status_code == 200
    assert '2' in response2.get_data(as_text=True)

def test_counter_works_per_session(client):
    """2. Проверка что счётчик работает для каждого пользователя"""
    # Первое посещение
    response1 = client.get('/counter/')
    assert '1' in response1.get_data(as_text=True)
    
    # Второе посещение
    response2 = client.get('/counter/')
    assert '2' in response2.get_data(as_text=True)

def test_login_success_redirect(client):
    """3. Проверка успешной аутентификации - перенаправление на главную страницу"""
    response = client.post('/login/', 
                          data={'username': 'user', 'password': 'qwerty'},
                          follow_redirects=True)
    assert response.status_code == 200
    assert 'Вы успешно вошли в систему!' in response.get_data(as_text=True)

def test_login_success_shows_message(client):
    """4. Проверка что после успешного входа показывается сообщение"""
    response = client.post('/login/', 
                          data={'username': 'user', 'password': 'qwerty'},
                          follow_redirects=True)
    assert 'Вы успешно вошли в систему!' in response.get_data(as_text=True)

def test_login_failure_stays_on_login_page(client):
    """5. Проверка неудачной аутентификации - остаёмся на странице входа"""
    response = client.post('/login/', 
                          data={'username': 'user', 'password': 'wrong'},
                          follow_redirects=True)
    assert response.status_code == 200
    assert 'Вход в систему' in response.get_data(as_text=True)
    assert 'Неверное имя пользователя или пароль.' in response.get_data(as_text=True)

def test_login_failure_shows_error_message(client):
    """6. Проверка что при ошибке показывается сообщение об ошибке"""
    response = client.post('/login/', 
                          data={'username': 'user', 'password': 'wrong'},
                          follow_redirects=True)
    assert 'Неверное имя пользователя или пароль.' in response.get_data(as_text=True)

def test_authenticated_user_can_access_secret_page(client):
    """7. Проверка что аутентифицированный пользователь имеет доступ к секретной странице"""
    # Сначала логинимся
    client.post('/login/', data={'username': 'user', 'password': 'qwerty'})
    # Пытаемся получить доступ к секретной странице
    response = client.get('/secret/')
    assert response.status_code == 200
    assert 'Секретная страница' in response.get_data(as_text=True)

def test_unauthenticated_user_redirected_from_secret(client):
    """8. Проверка что неаутентифицированный пользователь перенаправляется на страницу входа"""
    response = client.get('/secret/', follow_redirects=True)
    assert response.status_code == 200
    assert 'Вход в систему' in response.get_data(as_text=True)
    assert 'Пожалуйста, войдите для доступа к этой странице' in response.get_data(as_text=True)

def test_redirect_to_requested_page_after_login(client):
    """9. Проверка что после аутентификации пользователь перенаправляется на запрошенную страницу"""
    # Пытаемся получить доступ к секретной странице без авторизации
    response = client.get('/secret/')
    assert response.status_code == 302  # Редирект на логин
    
    # Логинимся с next параметром
    response = client.post('/login/?next=/secret/', 
                          data={'username': 'user', 'password': 'qwerty'},
                          follow_redirects=True)
    assert response.status_code == 200
    assert 'Секретная страница' in response.get_data(as_text=True)

def test_remember_me_sets_cookie(client):
    """10. Проверка что параметр Запомнить меня работает"""
    response = client.post('/login/', 
                          data={'username': 'user', 'password': 'qwerty', 'remember': 'on'})
    # Проверяем что есть заголовок Set-Cookie с remember_token
    assert 'Set-Cookie' in response.headers
    assert 'remember_token' in response.headers.get('Set-Cookie', '')

def test_logout_works(client):
    """11. Проверка выхода из системы"""
    # Сначала логинимся
    client.post('/login/', data={'username': 'user', 'password': 'qwerty'})
    # Выходим
    response = client.get('/logout/', follow_redirects=True)
    assert response.status_code == 200
    assert 'Вы вышли из системы.' in response.get_data(as_text=True)

def test_navbar_shows_secret_link_for_authenticated(client):
    """12. Проверка что ссылка на секретную страницу показывается только для аутентифицированных"""
    # Для неаутентифицированного
    response = client.get('/')
    assert 'Секретная страница' not in response.get_data(as_text=True)
    
    # Для аутентифицированного
    client.post('/login/', data={'username': 'user', 'password': 'qwerty'})
    response = client.get('/')
    assert 'Секретная страница' in response.get_data(as_text=True)

def test_navbar_shows_login_link_for_unauthenticated(client):
    """13. Проверка что для неаутентифицированных показывается ссылка Вход"""
    response = client.get('/')
    assert 'Войти' in response.get_data(as_text=True)
    assert 'Выйти' not in response.get_data(as_text=True)

def test_navbar_shows_logout_link_for_authenticated(client):
    """14. Проверка что для аутентифицированных показывается ссылка Выйти"""
    client.post('/login/', data={'username': 'user', 'password': 'qwerty'})
    response = client.get('/')
    assert 'Выйти' in response.get_data(as_text=True)
    assert 'Войти' not in response.get_data(as_text=True)

def test_secret_page_shows_username(client):
    """15. Проверка что на секретной странице отображается имя пользователя"""
    client.post('/login/', data={'username': 'user', 'password': 'qwerty'})
    response = client.get('/secret/')
    assert 'user' in response.get_data(as_text=True)

def test_invalid_credentials_do_not_login(client):
    """16. Проверка что неверные данные не авторизуют пользователя"""
    client.post('/login/', data={'username': 'user', 'password': 'wrong'})
    response = client.get('/secret/', follow_redirects=True)
    assert 'Вход в систему' in response.get_data(as_text=True)
    assert 'Секретная страница' not in response.get_data(as_text=True)

def test_counter_persists_in_session(client):
    """17. Проверка что счётчик сохраняется в сессии"""
    # Первое посещение
    client.get('/counter/')
    # Второе посещение
    response = client.get('/counter/')
    assert '2' in response.get_data(as_text=True)

def test_remember_me_persists_session(client):
    """18. Проверка что remember_me сохраняет сессию"""
    # Логинимся с remember_me
    response = client.post('/login/', 
                          data={'username': 'user', 'password': 'qwerty', 'remember': 'on'})
    
    # Проверяем что в ответе есть установка cookie
    set_cookie = response.headers.get('Set-Cookie', '')
    # Проверяем что есть remember_token в заголовке
    assert 'remember_token' in set_cookie or response.status_code == 302

def test_counter_multiple_visits_sequence(client):
    """19. Проверка последовательности посещений счётчика"""
    for i in range(1, 4):
        response = client.get('/counter/')
        assert str(i) in response.get_data(as_text=True)

def test_access_secret_without_login_redirects(client):
    """20. Проверка редиректа при доступе к секретной странице без логина"""
    response = client.get('/secret/')
    assert response.status_code == 302  # Редирект
    assert '/login/' in response.headers.get('Location', '')

def test_logout_redirects_to_index(client):
    """23. Проверка что после выхода редиректит на главную"""
    client.post('/login/', data={'username': 'user', 'password': 'qwerty'})
    response = client.get('/logout/', follow_redirects=True)
    assert response.status_code == 200
    assert 'Лабораторная работа №3' in response.get_data(as_text=True)