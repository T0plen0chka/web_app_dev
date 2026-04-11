from flask import Flask, request, render_template, make_response
from datetime import datetime
from functools import lru_cache

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Данные постов
@lru_cache(maxsize=1)
def get_posts():
    return [
        {
            'title': 'Введение в информационную безопасность',
            'text': 'Информационная безопасность — это практика защиты информации от несанкционированного доступа, использования, раскрытия, искажения, изменения, исследования, записи или уничтожения. Это универсальная проблема, затрагивающая как организации, так и частных лиц.\n\nЦифровая трансформация делает вопросы кибербезопасности более актуальными, чем когда-либо. Каждый день миллиарды устройств подключаются к интернету, создавая новые векторы атак для злоумышленников.\n\nПонимание основ информационной безопасности сегодня необходимо каждому ИТ-специалисту, независимо от его специализации.',
            'author': 'Скрынникова Полина Андреевна',
            'date': datetime(2025, 2, 15),
            'image_id': 'security-intro.jpg',
            'comments': [
                {
                    'author': 'Алексей Смирнов',
                    'text': 'Очень полезная статья! Жду продолжения.',
                    'replies': [
                        {'author': 'Автор', 'text': 'Спасибо за отзыв! Следующая часть уже готовится.'}
                    ]
                },
                {
                    'author': 'Мария Иванова',
                    'text': 'А не могли бы вы подробнее рассказать о SOC?',
                    'replies': []
                }
            ]
        },
        {
            'title': 'Основы криптографии',
            'text': 'Криптография — это наука о методах обеспечения конфиденциальности, целостности данных, аутентификации и неотказуемости с использованием математических алгоритмов. Она лежит в основе большинства современных протоколов безопасности.\n\nСимметричное и асимметричное шифрование, хеш-функции, электронные подписи — вот базовые инструменты, которые должен знать каждый специалист по информационной безопасности.\n\nВ этой статье мы рассмотрим основные принципы работы этих механизмов и их практическое применение.',
            'author': 'Скрынникова Полина Андреевна',
            'date': datetime(2025, 2, 20),
            'image_id': 'cryptography.jpg',
            'comments': [
                {
                    'author': 'Дмитрий Петров',
                    'text': 'Отличный материал! Особенно про асимметричное шифрование.',
                    'replies': []
                }
            ]
        },
        {
            'title': 'Безопасность веб-приложений',
            'text': 'Веб-приложения являются одной из основных целей для злоумышленников. OWASP Top 10 — это стандартный документ для осведомленности разработчиков о наиболее критических рисках безопасности веб-приложений.\n\nИнъекции, нарушение аутентификации, XSS, небезопасная десериализация — эти уязвимости продолжают занимать верхние строчки рейтинга.\n\nВ статье разбираются основные типы атак и методы защиты от них.',
            'author': 'Скрынникова Полина Андреевна',
            'date': datetime(2025, 2, 25),
            'image_id': 'web-security.jpg',
            'comments': []
        }
    ]

@app.route('/')
def index():
    return render_template('index.html', title='Главная')

@app.route('/posts')
def posts():
    posts = get_posts()
    return render_template('posts.html', title='Посты', posts=posts)

@app.route('/posts/<int:index>')
def post(index):
    posts = get_posts()
    if index < 0 or index >= len(posts):
        return render_template('404.html'), 404
    return render_template('post.html', title=posts[index]['title'], post=posts[index])

@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')

# ========== НОВЫЕ МАРШРУТЫ ==========

@app.route('/url-params')
def url_params():
    """Страница отображения параметров URL"""
    params = dict(request.args)
    return render_template('url_params.html', title='Параметры URL', params=params)

@app.route('/headers')
def headers_page():
    """Страница отображения заголовков запроса"""
    headers = dict(request.headers)
    return render_template('headers.html', title='Заголовки запроса', headers=headers)

@app.route('/cookies')
def cookies_page():
    """Страница для работы с cookies"""
    cookie_value = request.cookies.get('test_cookie')
    
    response = make_response(render_template('cookies.html', title='Cookie', cookie_value=cookie_value))
    
    if cookie_value is None:
        response.set_cookie('test_cookie', 'set_by_server_' + datetime.now().strftime('%Y%m%d%H%M%S'), max_age=3600)
    else:
        response.set_cookie('test_cookie', '', expires=0)
    
    return response

@app.route('/form-params', methods=['GET', 'POST'])
def form_params():
    """Страница с формой для отправки параметров"""
    form_data = None
    if request.method == 'POST':
        form_data = dict(request.form)
    return render_template('form_params.html', title='Параметры формы', form_data=form_data)

def validate_phone(phone: str):
    """
    Валидация номера телефона.
    Возвращает (is_valid, formatted_phone, error_message)
    """
    # Разрешенные символы: цифры, пробелы, (), -, ., +
    allowed_chars = set('0123456789 ()-.+')
    
    # Проверка на недопустимые символы
    for char in phone:
        if char not in allowed_chars:
            return False, None, "Недопустимый ввод. В номере телефона встречаются недопустимые символы."
    
    # Извлекаем только цифры
    digits = [c for c in phone if c.isdigit()]
    digit_count = len(digits)
    
    # Проверка количества цифр
    if digit_count == 11:
        # 11 цифр - должна начинаться с 7 или 8
        if digits[0] not in ['7', '8']:
            return False, None, "Недопустимый ввод. Неверное количество цифр."
        
        # Убираем первую цифру (7 или 8)
        number = digits[1:]
        
        # Форматируем как 8-***-***-**-**
        formatted = f"8-{number[0]}{number[1]}{number[2]}-{number[3]}{number[4]}{number[5]}-{number[6]}{number[7]}-{number[8]}{number[9]}"
        return True, formatted, None
        
    elif digit_count == 10:
        # 10 цифр - обычный номер, добавляем 8 в начало
        formatted = f"8-{digits[0]}{digits[1]}{digits[2]}-{digits[3]}{digits[4]}{digits[5]}-{digits[6]}{digits[7]}-{digits[8]}{digits[9]}"
        return True, formatted, None
    else:
        return False, None, "Недопустимый ввод. Неверное количество цифр."

@app.route('/phone-validation', methods=['GET', 'POST'])
def phone_validation():
    """Страница валидации номера телефона"""
    error = None
    formatted_phone = None
    submitted_phone = None
    
    if request.method == 'POST':
        submitted_phone = request.form.get('phone', '')
        is_valid, formatted, error_msg = validate_phone(submitted_phone)
        
        if is_valid:
            formatted_phone = formatted
        else:
            error = error_msg
    
    return render_template('phone_validation.html', 
                         title='Проверка номера телефона',
                         error=error,
                         formatted_phone=formatted_phone,
                         submitted_phone=submitted_phone)

if __name__ == '__main__':
    app.run(debug=True)