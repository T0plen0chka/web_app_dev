# 1. Проверка страницы параметров URL
def test_url_params_page(client):
    response = client.get("/url-params?name=John&age=30&city=Moscow")
    assert response.status_code == 200
    assert "name" in response.text
    assert "John" in response.text
    assert "age" in response.text
    assert "30" in response.text

# 2. Проверка страницы заголовков
def test_headers_page(client):
    response = client.get("/headers")
    assert response.status_code == 200
    assert "User-Agent" in response.text

# 3. Проверка установки и удаления cookie
def test_cookie_set_and_delete(client):
    # Первый запрос - cookie должен установиться
    response1 = client.get("/cookies")
    assert 'test_cookie' in response1.headers.get('Set-Cookie', '')
    
    # Второй запрос - cookie должен удалиться
    response2 = client.get("/cookies")
    assert 'test_cookie=;' in response2.headers.get('Set-Cookie', '') or 'test_cookie=' in response2.headers.get('Set-Cookie', '')

# 4. Проверка страницы параметров формы (GET)
def test_form_params_page_get(client):
    response = client.get("/form-params")
    assert response.status_code == 200
    assert "Отправить данные формы" in response.text

# 5. Проверка отправки формы (POST)
def test_form_params_post(client):
    response = client.post("/form-params", data={
        'name': 'Test User',
        'email': 'test@example.com',
        'message': 'Hello World'
    })
    assert response.status_code == 200
    assert "Test User" in response.text
    assert "test@example.com" in response.text
    assert "Hello World" in response.text

# 6. Проверка валидации телефона - корректный номер с +7
def test_phone_validation_valid_plus7(client):
    response = client.post("/phone-validation", data={'phone': '+7 (123) 456-75-90'})
    assert response.status_code == 200
    assert "Номер корректен" in response.text
    assert "8-123-456-75-90" in response.text

# 7. Проверка валидации телефона - корректный номер с 8
def test_phone_validation_valid_8(client):
    response = client.post("/phone-validation", data={'phone': '8(123)4567590'})
    assert response.status_code == 200
    assert "Номер корректен" in response.text
    assert "8-123-456-75-90" in response.text

# 8. Проверка валидации телефона - корректный 10-значный номер
def test_phone_validation_valid_10_digits(client):
    response = client.post("/phone-validation", data={'phone': '123.456.75.90'})
    assert response.status_code == 200
    assert "Номер корректен" in response.text

# 10. Проверка валидации телефона - недопустимые символы
def test_phone_validation_invalid_chars(client):
    response = client.post("/phone-validation", data={'phone': '123abc456'})
    assert response.status_code == 200
    assert "is-invalid" in response.text
    assert "встречаются недопустимые символы" in response.text

# 10. Проверка валидации телефона - неверное количество цифр
def test_phone_validation_wrong_digit_count(client):
    response = client.post("/phone-validation", data={'phone': '12345'})
    assert response.status_code == 200
    assert "is-invalid" in response.text
    assert "Неверное количество цифр" in response.text

# 11. Проверка валидации телефона - 11 цифр не с 7 или 8
def test_phone_validation_invalid_11_digits_start(client):
    response = client.post("/phone-validation", data={'phone': '91234567890'})
    assert response.status_code == 200
    assert "is-invalid" in response.text
    assert "Неверное количество цифр" in response.text

# 12. Проверка валидации телефона - корректный номер с пробелами
def test_phone_validation_valid_with_spaces(client):
    response = client.post("/phone-validation", data={'phone': '+7 123 456 75 90'})
    assert response.status_code == 200
    assert "Номер корректен" in response.text

# 13. Проверка страницы валидации - отображение ошибки с Bootstrap классом
def test_phone_validation_error_bootstrap_class(client):
    response = client.post("/phone-validation", data={'phone': 'invalid'})
    assert response.status_code == 200
    assert 'is-invalid' in response.text
    assert 'invalid-feedback' in response.text

# 14. Проверка, что на страницах есть навигационное меню с новыми пунктами
def test_navbar_has_new_pages(client):
    response = client.get("/")
    assert "Параметры URL" in response.text
    assert "Заголовки запроса" in response.text
    assert "Cookie" in response.text
    assert "Параметры формы" in response.text
    assert "Проверка телефона" in response.text

# 15. Проверка валидации телефона - пустая строка
def test_phone_validation_empty_string(client):
    response = client.post("/phone-validation", data={'phone': ''})
    assert response.status_code == 200
    assert "is-invalid" in response.text