from models import db, DailyRecord, MealRecord
from datetime import datetime, date


class RecordService:
    @staticmethod
    def create_daily_record(user_id, record_date, weight=None, exercise=False,
                           exercise_name=None, exercise_duration=None,
                           hunger_times=0, feedback=None):
        record = DailyRecord(
            user_id=user_id,
            record_date=record_date,
            weight=weight,
            exercise=exercise,
            exercise_name=exercise_name,
            exercise_duration=exercise_duration,
            hunger_times=hunger_times,
            feedback=feedback,
            create_time=datetime.utcnow()
        )
        db.session.add(record)
        db.session.commit()
        return record

    @staticmethod
    def get_daily_record(user_id, record_date):
        return DailyRecord.query.filter_by(
            user_id=user_id,
            record_date=record_date
        ).first()

    @staticmethod
    def get_daily_record_by_id(record_id, user_id):
        return DailyRecord.query.filter_by(
            id=record_id,
            user_id=user_id
        ).first()

    @staticmethod
    def get_all_records(user_id, limit=None):
        query = DailyRecord.query.filter_by(user_id=user_id).order_by(DailyRecord.record_date.desc())
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def update_daily_record(record_id, user_id, **kwargs):
        record = DailyRecord.query.filter_by(id=record_id, user_id=user_id).first()
        if not record:
            return None

        for key, value in kwargs.items():
            if hasattr(record, key) and value is not None:
                setattr(record, key, value)

        db.session.commit()
        return record

    @staticmethod
    def delete_daily_record(record_id, user_id):
        record = DailyRecord.query.filter_by(id=record_id, user_id=user_id).first()
        if not record:
            return False

        db.session.delete(record)
        db.session.commit()
        return True

    @staticmethod
    def add_meal_record(daily_record_id, meal_type, fullness=None, description=None):
        meal = MealRecord(
            daily_record_id=daily_record_id,
            meal_type=meal_type,
            fullness=fullness,
            description=description,
            create_time=datetime.utcnow()
        )
        db.session.add(meal)
        db.session.commit()
        return meal

    @staticmethod
    def get_meal_records(daily_record_id):
        return MealRecord.query.filter_by(daily_record_id=daily_record_id).all()

    @staticmethod
    def update_meal_record(meal_id, **kwargs):
        meal = MealRecord.query.get(meal_id)
        if not meal:
            return None

        for key, value in kwargs.items():
            if hasattr(meal, key) and value is not None:
                setattr(meal, key, value)

        db.session.commit()
        return meal

    @staticmethod
    def delete_meal_record(meal_id):
        meal = MealRecord.query.get(meal_id)
        if not meal:
            return False

        db.session.delete(meal)
        db.session.commit()
        return True
