from app.models import Review
from sqlalchemy import desc, asc

class ReviewRepository:
    def __init__(self, db):
        self.db = db
    
    def get_review_by_user_and_course(self, user_id, course_id):
        """Получить отзыв пользователя на конкретный курс"""
        return self.db.session.execute(
            self.db.select(Review).filter_by(user_id=user_id, course_id=course_id)
        ).scalar()
    
    def get_course_reviews_paginated(self, course_id, page=1, per_page=10, sort_by='newest'):
        """Получить отзывы курса с пагинацией и сортировкой"""
        query = self.db.select(Review).filter_by(course_id=course_id)
        
        # Применяем сортировку
        if sort_by == 'newest':
            query = query.order_by(desc(Review.created_at))
        elif sort_by == 'positive_first':
            query = query.order_by(desc(Review.rating), desc(Review.created_at))
        elif sort_by == 'negative_first':
            query = query.order_by(asc(Review.rating), desc(Review.created_at))
        
        return self.db.paginate(query, page=page, per_page=per_page)
    
    def get_recent_reviews(self, course_id, limit=5):
        """Получить последние N отзывов"""
        query = self.db.select(Review).filter_by(course_id=course_id).order_by(desc(Review.created_at)).limit(limit)
        return self.db.session.execute(query).scalars().all()
    
    def add_review(self, user_id, course_id, rating, text):
        """Добавить новый отзыв"""
        review = Review(
            user_id=user_id,
            course_id=course_id,
            rating=rating,
            text=text
        )
        
        try:
            self.db.session.add(review)
            self.db.session.commit()
            return review
        except Exception as e:
            self.db.session.rollback()
            raise e