from app import create_app
from app.models import db, User, Category, Course

app = create_app()

with app.app_context():
    print("Настройка базы данных...")
    
    # 1. Создаем таблицы (если не созданы)
    db.create_all()
    print("✓ Таблицы созданы")
    
    # 2. Добавляем категории
    categories_data = [
        'Программирование',
        'Математика', 
        'Языкознание',
        'Дизайн',
        'Маркетинг',
        'Управление проектами'
    ]
    
    added_categories = []
    for cat_name in categories_data:
        # Используем db.session.execute вместо Category.query
        cat = db.session.execute(db.select(Category).filter_by(name=cat_name)).scalar()
        if not cat:
            cat = Category(name=cat_name)
            db.session.add(cat)
            added_categories.append(cat_name)
    
    if added_categories:
        print(f"✓ Добавлены категории: {', '.join(added_categories)}")
    else:
        print("✓ Категории уже существуют")
    
    # 3. Создаем пользователя
    user = db.session.execute(db.select(User).filter_by(login='ivan')).scalar()
    if not user:
        user = User(
            first_name='Иван',
            last_name='Петров',
            middle_name='Сергеевич',
            login='ivan'
        )
        user.set_password('qwerty123')
        db.session.add(user)
        print("✓ Создан пользователь: ivan / qwerty123")
    else:
        print("✓ Пользователь уже существует: ivan")
    
    # Сохраняем пользователя, чтобы получить его ID
    db.session.commit()
    
    # 4. Создаем тестовый курс (опционально)
    existing_course = db.session.execute(db.select(Course)).scalar()
    if not existing_course:
        # Получаем первую категорию и пользователя
        category = db.session.execute(db.select(Category)).scalar()
        
        if category and user:
            course = Course(
                name='Тестовый курс',
                short_desc='Это тестовый курс для проверки функционала отзывов',
                full_desc='Полное описание тестового курса. Здесь будет много полезной информации.',
                author_id=user.id,
                category_id=category.id,
                background_image_id='temp'  # временное значение
            )
            db.session.add(course)
            print("✓ Создан тестовый курс")
    
    # Сохраняем все изменения
    db.session.commit()
    
    # Получаем статистику
    categories_count = db.session.execute(db.select(db.func.count()).select_from(Category)).scalar()
    users_count = db.session.execute(db.select(db.func.count()).select_from(User)).scalar()
    courses_count = db.session.execute(db.select(db.func.count()).select_from(Course)).scalar()
    
    print("\n" + "="*50)
    print("Настройка завершена!")
    print("="*50)
    print(f"Категорий в БД: {categories_count}")
    print(f"Пользователей в БД: {users_count}")
    print(f"Курсов в БД: {courses_count}")
    print("\nДанные для входа:")
    print("  Логин: ivan")
    print("  Пароль: qwerty123")
    print("="*50)