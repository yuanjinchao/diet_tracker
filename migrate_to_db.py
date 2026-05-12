#!/usr/bin/env python3
"""
数据迁移脚本 - 将 records.json 迁移到 SQLite 数据库
"""

import json
import os
import sys
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, User, DailyRecord, MealRecord
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diet_tracker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app


def migrate(records_json_path, target_phone='18500367490'):
    app = create_app()

    with app.app_context():
        db.create_all()

        user = User.query.filter_by(phone=target_phone).first()
        if not user:
            print(f"错误: 用户 {target_phone} 不存在，请先注册")
            return False

        user_id = user.id
        print(f"找到用户 {target_phone}, user_id: {user_id}")

        if not os.path.exists(records_json_path):
            print(f"错误: 文件不存在 {records_json_path}")
            return False

        with open(records_json_path, 'r', encoding='utf-8') as f:
            records = json.load(f)

        migrated_days = 0
        migrated_meals = 0

        for record in records:
            record_date_str = record['date'].split(' ')[0]
            record_date = datetime.strptime(record_date_str, '%Y-%m-%d').date()

            existing = DailyRecord.query.filter_by(
                user_id=user_id,
                record_date=record_date
            ).first()

            if existing:
                daily_record = existing
            else:
                daily_record = DailyRecord(
                    user_id=user_id,
                    record_date=record_date,
                    weight=record.get('weight'),
                    exercise=record.get('exercise', False),
                    exercise_name=record.get('exercise_info', {}).get('name') if record.get('exercise_info') else None,
                    exercise_duration=record.get('exercise_info', {}).get('duration') if record.get('exercise_info') else None,
                    hunger_times=record.get('hunger', {}).get('times', 0) if record.get('hunger') else 0,
                    feedback=record.get('feedback'),
                    create_time=datetime.utcnow()
                )
                db.session.add(daily_record)
                db.session.commit()
                migrated_days += 1

            if 'food' in record:
                food = record['food']

                for meal_type in ['breakfast', 'lunch', 'dinner']:
                    if meal_type in food and food[meal_type].get('recorded'):
                        meal_data = food[meal_type]

                        existing_meal = MealRecord.query.filter_by(
                            daily_record_id=daily_record.id,
                            meal_type=meal_type
                        ).first()

                        if not existing_meal:
                            meal = MealRecord(
                                daily_record_id=daily_record.id,
                                meal_type=meal_type,
                                fullness=meal_data.get('fullness'),
                                description=meal_data.get('description'),
                                create_time=datetime.utcnow()
                            )
                            db.session.add(meal)
                            migrated_meals += 1

                db.session.commit()

        print(f"\n迁移完成!")
        print(f"- 每日记录: {migrated_days} 条")
        print(f"- 三餐记录: {migrated_meals} 条")
        return True


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    records_json = os.path.join(script_dir, 'data', 'records.json')

    target_phone = '18500367490'
    if len(sys.argv) > 1:
        target_phone = sys.argv[1]
    if len(sys.argv) > 2:
        records_json = sys.argv[2]

    print("=" * 50)
    print("减肥打卡 - 数据迁移工具")
    print("=" * 50)
    print(f"数据文件: {records_json}")
    print(f"目标用户手机号: {target_phone}")
    print("=" * 50)

    migrate(records_json, target_phone)
