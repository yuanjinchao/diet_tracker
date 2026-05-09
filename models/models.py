from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    daily_records = db.relationship('DailyRecord', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'phone': self.phone,
            'create_time': self.create_time.isoformat() if self.create_time else None
        }


class DailyRecord(db.Model):
    __tablename__ = 'daily_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    weight = db.Column(db.Float)
    exercise = db.Column(db.Boolean, default=False)
    exercise_name = db.Column(db.String(50))
    exercise_duration = db.Column(db.Integer)
    hunger_times = db.Column(db.Integer, default=0)
    feedback = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    meals = db.relationship('MealRecord', backref='daily_record', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_meals=False):
        record_date_str = self.record_date.isoformat() if self.record_date else None
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'record_date': record_date_str,
            'date': record_date_str,
            'weight': self.weight,
            'exercise': self.exercise,
            'exercise_name': self.exercise_name,
            'exercise_duration': self.exercise_duration,
            'hunger_times': self.hunger_times,
            'feedback': self.feedback,
            'create_time': self.create_time.isoformat() if self.create_time else None
        }
        
        if include_meals:
            result['meals'] = [meal.to_dict() for meal in self.meals]
            
            food_data = {
                'breakfast': {'recorded': False, 'fullness': 7, 'description': ''},
                'lunch': {'recorded': False, 'fullness': 7, 'description': ''},
                'dinner': {'recorded': False, 'fullness': 7, 'description': ''}
            }
            
            for meal in self.meals:
                if meal.meal_type in food_data:
                    food_data[meal.meal_type] = {
                        'recorded': True,
                        'fullness': meal.fullness or 7,
                        'description': meal.description or ''
                    }
            
            result['food'] = food_data
            
            if self.exercise_name or self.exercise_duration:
                result['exercise_info'] = {
                    'name': self.exercise_name or '跑步',
                    'duration': self.exercise_duration or 30
                }
            
            result['hunger'] = {'times': self.hunger_times or 0}
        
        return result


class MealRecord(db.Model):
    __tablename__ = 'meal_records'

    id = db.Column(db.Integer, primary_key=True)
    daily_record_id = db.Column(db.Integer, db.ForeignKey('daily_records.id'), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    fullness = db.Column(db.Integer)
    description = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'daily_record_id': self.daily_record_id,
            'meal_type': self.meal_type,
            'fullness': self.fullness,
            'description': self.description,
            'create_time': self.create_time.isoformat() if self.create_time else None
        }
