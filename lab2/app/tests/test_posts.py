import pytest
from datetime import datetime

def test_index_status(client):
    """1. Проверка главной страницы"""
    assert client.get("/").status_code == 200

def test_posts_list_status(client):
    """2. Проверка страницы списка постов"""
    assert client.get("/posts").status_code == 200

def test_about_status(client):
    """3. Проверка страницы Об авторе"""
    assert client.get("/about").status_code == 200

def test_post_detail_template(client, captured_templates):
    """4. Проверка использования шаблона для страницы поста"""
    with captured_templates as templates:
        client.get("/posts/0")
        assert any(t[0].name == 'post.html' for t in templates)

def test_post_context_data(client, captured_templates):
    """5. Проверка передачи объекта post в контекст шаблона"""
    with captured_templates as templates:
        client.get("/posts/0")
        if templates:
            _, context = templates[0]
            assert 'post' in context

def test_post_text_content(client):
    """6. Проверка наличия контента поста"""
    response = client.get("/posts/0")
    assert response.status_code == 200
    assert len(response.get_data(as_text=True)) > 500

def test_post_image_tag(client):
    """7. Проверка наличия изображения"""
    response = client.get("/posts/0")
    assert "<img" in response.get_data(as_text=True)

def test_comment_form_exists(client):
    """8. Проверка наличия формы для комментариев"""
    response = client.get("/posts/0")
    assert "Оставьте комментарий" in response.get_data(as_text=True)

def test_submit_button_exists(client):
    """9. Проверка наличия кнопки отправки формы"""
    response = client.get("/posts/0")
    assert "Отправить" in response.get_data(as_text=True)

def test_date_format_display(client, mocker):
    """10. Проверка формата даты (ДД.ММ.ГГГГ)"""
    fixed_date = datetime(2026, 3, 27)
    mock_post = {
        'title': 'Test', 'text': 'Test text', 'author': 'Admin',
        'date': fixed_date, 'image_id': 'test.jpg', 
        'comments': []
    }
    mocker.patch("app.get_posts", return_value=[mock_post])
    response = client.get("/posts/0")
    assert "27.03.2026" in response.get_data(as_text=True)

def test_error_404_on_invalid_post(client):
    """11. Проверка обработки несуществующего индекса (404)"""
    response = client.get("/posts/999")
    assert response.status_code == 404

def test_footer_name_correct(client):
    """12. Проверка ФИО автора в футер"""
    response = client.get("/")
    assert "Скрынникова Полина Андреевна" in response.get_data(as_text=True)

def test_footer_group_correct(client):
    """13. Проверка номера группы в футере"""
    response = client.get("/")
    assert "241-371" in response.get_data(as_text=True)

def test_navbar_present(client):
    """14. Проверка наличия навигационной панели"""
    response = client.get("/")
    assert "navbar" in response.get_data(as_text=True)

def test_url_params_page(client):
    """15. Проверка страницы параметров URL"""
    response = client.get("/url-params?name=John&age=30")
    assert response.status_code == 200
    data = response.get_data(as_text=True)
    assert "name" in data
    assert "John" in data

def test_headers_page(client):
    """16. Проверка страницы заголовков"""
    response = client.get("/headers")
    assert response.status_code == 200
    assert "User-Agent" in response.get_data(as_text=True)

def test_phone_validation_valid(client):
    """17. Проверка валидации телефона - корректный номер"""
    response = client.post("/phone-validation", 
                          data={'phone': '+7 (123) 456-75-90'},
                          follow_redirects=True)
    assert "Номер корректен" in response.get_data(as_text=True)