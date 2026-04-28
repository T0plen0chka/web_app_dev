import pytest
from app.models import db, User, Course, Review
from app.repositories import ReviewRepository

class TestReviews:
    def test_create_review(self, app, test_user, test_course):
        """Тест создания отзыва"""
        with app.app_context():
            review_repo = ReviewRepository(db)
            
            review = review_repo.add_review(
                user_id=test_user.id,
                course_id=test_course.id,
                rating=5,
                text="Отличный курс!"
            )
            
            assert review is not None
            assert review.rating == 5
            assert review.text == "Отличный курс!"
            assert review.user_id == test_user.id
            assert review.course_id == test_course.id
    
    def test_get_review_by_user_and_course(self, app, test_user, test_course, test_review):
        """Тест получения отзыва по пользователю и курсу"""
        with app.app_context():
            review_repo = ReviewRepository(db)
            
            review = review_repo.get_review_by_user_and_course(test_user.id, test_course.id)
            
            assert review is not None
            assert review.id == test_review.id
    
    def test_get_course_reviews_paginated(self, app, test_course, test_reviews):
        """Тест пагинации отзывов"""
        with app.app_context():
            review_repo = ReviewRepository(db)
            
            # Тест первой страницы
            pagination = review_repo.get_course_reviews_paginated(
                test_course.id, page=1, per_page=5, sort_by='newest'
            )
            
            assert pagination.items is not None
            assert len(pagination.items) <= 5
    
    def test_course_rating_update(self, app, test_course, test_user):
        """Тест обновления рейтинга курса при добавлении отзыва"""
        with app.app_context():
            review_repo = ReviewRepository(db)
            
            initial_rating = test_course.rating
            
            # Добавляем отзыв с оценкой 5
            review_repo.add_review(test_user.id, test_course.id, 5, "Отлично!")
            test_course.update_rating()
            db.session.commit()
            
            assert test_course.rating_sum == 5
            assert test_course.rating_num == 1
            assert test_course.rating == 5.0

class TestReviewRoutes:
    def test_reviews_page_access(self, client, test_course):
        """Тест доступа к странице отзывов"""
        response = client.get(f'/courses/{test_course.id}/reviews')
        assert response.status_code == 200
    
    def test_create_review_authenticated(self, client, test_user, test_course):
        """Тест создания отзыва авторизованным пользователем"""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(test_user.id)
        
        response = client.post(
            f'/courses/{test_course.id}/reviews/create',
            data={'rating': 5, 'text': 'Замечательный курс!'},
            follow_redirects=True
        )
        
        assert response.status_code == 200
        
        # Проверяем, что отзыв создался
        with client.application.app_context():
            review_repo = ReviewRepository(db)
            review = review_repo.get_review_by_user_and_course(test_user.id, test_course.id)
            assert review is not None
            assert review.rating == 5
    
    def test_create_review_unauthenticated(self, client, test_course):
        """Тест создания отзыва неавторизованным пользователем"""
        response = client.post(
            f'/courses/{test_course.id}/reviews/create',
            data={'rating': 5, 'text': 'Замечательный курс!'},
            follow_redirects=True
        )
        
        # Должен быть редирект на страницу логина
        assert response.status_code == 200
        assert 'login' in response.request.path
    
    def test_duplicate_review(self, client, test_user, test_course, test_review):
        """Тест повторного создания отзыва"""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(test_user.id)
        
        response = client.post(
            f'/courses/{test_course.id}/reviews/create',
            data={'rating': 4, 'text': 'Еще один отзыв'},
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert 'Вы уже оставили отзыв' in response.data.decode('utf-8')

# Фикстуры для тестов
@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(
            first_name='Тест',
            last_name='Тестов',
            login='testuser'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_course(app, test_user):
    with app.app_context():
        course = Course(
            name='Тестовый курс',
            short_desc='Краткое описание',
            full_desc='Полное описание',
            author_id=test_user.id,
            category_id=1,  # Предполагается, что категория существует
            background_image_id='test-image-id'
        )
        db.session.add(course)
        db.session.commit()
        return course

@pytest.fixture
def test_review(app, test_user, test_course):
    with app.app_context():
        review = Review(
            user_id=test_user.id,
            course_id=test_course.id,
            rating=5,
            text='Тестовый отзыв'
        )
        db.session.add(review)
        db.session.commit()
        return review

@pytest.fixture
def test_reviews(app, test_course, test_user):
    with app.app_context():
        reviews = []
        for i in range(10):
            review = Review(
                user_id=test_user.id,
                course_id=test_course.id,
                rating=i % 5 + 1,
                text=f'Тестовый отзыв {i}'
            )
            reviews.append(review)
            db.session.add(review)
        db.session.commit()
        return reviews