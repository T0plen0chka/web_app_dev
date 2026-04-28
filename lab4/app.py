from flask import Flask, render_template, session, redirect, url_for, request, flash, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from models import db, User, Role
from forms import UserCreateForm, UserEditForm, ChangePasswordForm
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация БД
db.init_app(app)

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
login_manager.login_message_category = 'warning'

class UserLogin(UserMixin):
    def __init__(self, user):
        self.id = user.id
        self.username = user.username
        self.role_id = user.role_id

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if user:
        return UserLogin(user)
    return None

# Контекстный процессор для передачи данных в шаблоны
@app.context_processor
def utility_processor():
    return {
        'is_authenticated': current_user.is_authenticated,
        'current_user': current_user
    }

# Создание таблиц БД и добавление начальных данных
@app.before_request
def create_tables():
    db.create_all()
    # Добавляем роли по умолчанию
    if Role.query.count() == 0:
        roles = [
            Role(name='admin', description='Администратор системы'),
            Role(name='user', description='Обычный пользователь'),
            Role(name='guest', description='Гостевой доступ')
        ]
        for role in roles:
            db.session.add(role)
        db.session.commit()
    
    # Добавляем тестового пользователя
    if User.query.filter_by(username='admin').first() is None:
        admin_user = User(
            username='admin',
            password_hash=generate_password_hash('Admin123!'),
            last_name='Администратор',
            first_name='Системный',
            patronymic='',
            role_id=1,
            created_at=datetime.now()
        )
        db.session.add(admin_user)
        db.session.commit()

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            user_login = UserLogin(user)
            login_user(user_login, remember=remember)
            flash('Вы успешно вошли в систему!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль.', 'danger')
    
    return render_template('login.html')

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))

@app.route('/user/create/', methods=['GET', 'POST'])
@login_required
def user_create():
    form = UserCreateForm()
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]
    
    if form.validate_on_submit():
        # Проверка уникальности логина
        if User.query.filter_by(username=form.username.data).first():
            flash('Пользователь с таким логином уже существует.', 'danger')
            return render_template('user_form.html', form=form, title='Создание пользователя')
        
        user = User(
            username=form.username.data,
            password_hash=generate_password_hash(form.password.data),
            last_name=form.last_name.data,
            first_name=form.first_name.data,
            patronymic=form.patronymic.data or '',
            role_id=form.role_id.data,
            created_at=datetime.now()
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Пользователь успешно создан!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании пользователя: {str(e)}', 'danger')
    
    return render_template('user_form.html', form=form, title='Создание пользователя')

@app.route('/user/<int:user_id>/')
def user_view(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_view.html', user=user)

@app.route('/user/<int:user_id>/edit/', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]
    
    if form.validate_on_submit():
        user.last_name = form.last_name.data
        user.first_name = form.first_name.data
        user.patronymic = form.patronymic.data or ''
        user.role_id = form.role_id.data
        
        try:
            db.session.commit()
            flash('Пользователь успешно обновлён!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении пользователя: {str(e)}', 'danger')
    
    return render_template('user_form.html', form=form, title='Редактирование пользователя', edit_mode=True)

@app.route('/user/<int:user_id>/delete/', methods=['POST'])
@login_required
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    
    # Не даём удалить самого себя
    if current_user.id == user_id:
        flash('Вы не можете удалить свою собственную учётную запись.', 'danger')
        return redirect(url_for('index'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь успешно удалён!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении пользователя: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/change-password/', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        
        # Проверка старого пароля
        if not check_password_hash(user.password_hash, form.old_password.data):
            flash('Неверный текущий пароль.', 'danger')
            return render_template('change_password.html', form=form)
        
        # Смена пароля
        user.password_hash = generate_password_hash(form.new_password.data)
        
        try:
            db.session.commit()
            flash('Пароль успешно изменён!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при смене пароля: {str(e)}', 'danger')
    
    return render_template('change_password.html', form=form)

@app.route('/secret/')
@login_required
def secret():
    return render_template('secret.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)