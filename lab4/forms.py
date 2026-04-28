from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError
import re

def validate_password(form, field):
    """Валидация пароля"""
    password = field.data
    
    if len(password) < 8:
        raise ValidationError('Пароль должен содержать не менее 8 символов.')
    if len(password) > 128:
        raise ValidationError('Пароль не должен превышать 128 символов.')
    if ' ' in password:
        raise ValidationError('Пароль не должен содержать пробелов.')
    
    # Проверка на заглавные и строчные буквы
    if not re.search(r'[A-ZА-Я]', password):
        raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву.')
    if not re.search(r'[a-zа-я]', password):
        raise ValidationError('Пароль должен содержать хотя бы одну строчную букву.')
    
    # Проверка на цифры
    if not re.search(r'\d', password):
        raise ValidationError('Пароль должен содержать хотя бы одну цифру.')
    
    # Проверка допустимых символов
    allowed_chars = r'^[A-Za-zА-Яа-я0-9~!?@#$%^&*_\-+()\[\]{}><\/\\|"\'.,:;]+$'
    if not re.match(allowed_chars, password):
        raise ValidationError('Пароль содержит недопустимые символы.')

def validate_username(form, field):
    """Валидация логина"""
    username = field.data
    if len(username) < 5:
        raise ValidationError('Логин должен содержать не менее 5 символов.')
    if not re.match(r'^[A-Za-z0-9]+$', username):
        raise ValidationError('Логин может содержать только латинские буквы и цифры.')

class UserCreateForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message='Логин не может быть пустым.'),
        validate_username
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль не может быть пустым.'),
        validate_password
    ])
    last_name = StringField('Фамилия', validators=[
        DataRequired(message='Фамилия не может быть пустой.')
    ])
    first_name = StringField('Имя', validators=[
        DataRequired(message='Имя не может быть пустым.')
    ])
    patronymic = StringField('Отчество', validators=[])
    role_id = SelectField('Роль', coerce=int, validators=[
        DataRequired(message='Выберите роль.')
    ])

class UserEditForm(FlaskForm):
    last_name = StringField('Фамилия', validators=[
        DataRequired(message='Фамилия не может быть пустой.')
    ])
    first_name = StringField('Имя', validators=[
        DataRequired(message='Имя не может быть пустым.')
    ])
    patronymic = StringField('Отчество', validators=[])
    role_id = SelectField('Роль', coerce=int, validators=[
        DataRequired(message='Выберите роль.')
    ])

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[
        DataRequired(message='Введите старый пароль.')
    ])
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(message='Новый пароль не может быть пустым.'),
        validate_password
    ])
    confirm_password = PasswordField('Подтверждение пароля', validators=[
        DataRequired(message='Подтвердите новый пароль.')
    ])
    
    def validate_confirm_password(self, field):
        if self.new_password.data != field.data:
            raise ValidationError('Пароли не совпадают.')