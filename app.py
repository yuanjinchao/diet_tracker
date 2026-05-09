from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from models import db, User, DailyRecord, MealRecord
from services import UserService, RecordService
from datetime import datetime, date
import os
import random
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'diet-tracker-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diet_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

DATA_FILE = 'data/records.json'


def init_data_file():
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False)


def get_old_records():
    init_data_file()
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def analyze_food(food):
    food = food.lower()

    categories = {
        'high_calorie': ['蛋糕', '冰淇淋', '薯片', '炸鸡', '薯条', '汉堡', '披萨', '巧克力', '饼干', '糖果', '奶茶', '可乐', '雪碧'],
        'carb': ['米饭', '面条', '馒头', '面包', '包子', '饺子', '馄饨', '粥', '油条', '面饼'],
        'protein': ['鸡肉', '牛肉', '鱼肉', '鸡蛋', '虾', '豆腐', '瘦肉', '牛排'],
        'vegetable': ['白菜', '菠菜', '西兰花', '胡萝卜', '黄瓜', '番茄', '生菜', '芹菜', '青椒', '蘑菇'],
        'fruit': ['苹果', '香蕉', '橙子', '梨', '西瓜', '草莓', '葡萄', '芒果', '蓝莓']
    }

    result = {
        'has_high_calorie': any(item in food for item in categories['high_calorie']),
        'has_carb': any(item in food for item in categories['carb']),
        'has_protein': any(item in food for item in categories['protein']),
        'has_vegetable': any(item in food for item in categories['vegetable']),
        'has_fruit': any(item in food for item in categories['fruit']),
        'is_healthy': False
    }

    if (result['has_vegetable'] or result['has_fruit']) and not result['has_high_calorie']:
        result['is_healthy'] = True

    return result


def generate_feedback(record, all_records=None):
    feedback_parts = []

    weight = record.get('weight')
    meals = record.get('meals', [])
    exercise = record.get('exercise', False)
    exercise_name = record.get('exercise_name')
    exercise_duration = record.get('exercise_duration')
    hunger_times = record.get('hunger_times', 0)

    if all_records and len(all_records) >= 1:
        prev_weight = all_records[-1].get('weight')
        weight_change = weight - prev_weight if weight and prev_weight else 0
        if weight_change < -0.5:
            feedback_parts.append(random.choice([
                '体重下降了，太棒了！继续保持',
                '今天减重效果不错，再接再厉',
                '体重有明显下降，坚持就是胜利'
            ]))
        elif weight_change < -0.1:
            feedback_parts.append(random.choice([
                '体重稍微下降了一点，继续加油',
                '小有进步，保持这个势头',
                '今天控制得不错，继续保持'
            ]))
        elif weight_change > 0.5:
            feedback_parts.append(random.choice([
                '体重有点上升，明天要注意饮食和运动哦',
                '今天可能吃多了，明天调整一下',
                '体重增加了，需要控制一下'
            ]))
        elif weight_change > 0.1:
            feedback_parts.append(random.choice([
                '体重稍微上升，注意控制饮食',
                '今天摄入可能超标了，明天改进',
                '体重有点波动，保持平常心'
            ]))
        else:
            feedback_parts.append(random.choice([
                '体重保持稳定，继续努力',
                '体重没变，继续坚持就会有效果',
                '今天状态不错，保持住'
            ]))
    else:
        feedback_parts.append(random.choice([
            '开始记录，加油！',
            '希望你能坚持下去',
            '新的开始，祝你成功'
        ]))

    if meals:
        fullness_values = [m.get('fullness', 0) for m in meals if m.get('fullness', 0) > 0]

        if fullness_values:
            avg_fullness = sum(fullness_values) / len(fullness_values)
            if avg_fullness >= 8:
                feedback_parts.append(random.choice([
                    '今天每餐都吃得很饱，注意控制一下食量哦',
                    '饱腹感很强，明天可以稍微少吃点',
                    '吃了不少，明天适当减少一点'
                ]))
            elif avg_fullness >= 6:
                feedback_parts.append(random.choice([
                    '今天吃得刚刚好，保持这个状态',
                    '饱腹感适中，很健康的状态',
                    '饮食份量合适，继续保持'
                ]))
            elif avg_fullness >= 4:
                feedback_parts.append(random.choice([
                    '今天稍微有点饿，注意营养均衡',
                    '摄入稍微少了一点，要吃饱才有力气减肥',
                    '有点饿，记得吃够营养'
                ]))
            else:
                feedback_parts.append(random.choice([
                    '今天感觉挺饿的，别太亏待自己',
                    '摄入有点少，记得吃饱才能更好减肥',
                    '饿了就要吃，别硬撑'
                ]))

    if hunger_times > 0:
        if hunger_times >= 4:
            feedback_parts.append(random.choice([
                f'今天饿了 {hunger_times} 次，确实比较馋，建议调整饮食结构',
                f'饿了 {hunger_times} 次，可以考虑加餐或调整份量',
                f'一天饿了 {hunger_times} 次，注意控制饥饿感'
            ]))
        elif hunger_times >= 2:
            feedback_parts.append(random.choice([
                f'今天饿了 {hunger_times} 次，还算正常范围',
                f'有 {hunger_times} 次饥饿感，注意多喝水',
                f'饿了 {hunger_times} 次，可以忍受的话就没问题'
            ]))
        else:
            feedback_parts.append(random.choice([
                '今天只饿了 1 次，不错！',
                '几乎没怎么饿，状态很好',
                '饱腹感不错，继续保持'
            ]))

    food_descriptions = [m.get('description', '') for m in meals if m.get('description')]
    food_text = ' '.join(food_descriptions)
    food_analysis = analyze_food(food_text)

    if food_analysis['has_high_calorie']:
        feedback_parts.append(random.choice([
            '今天高热量食物有点多，明天可以清淡一点',
            '吃了不少高热量的，明天注意控制',
            '高热量食物要适量哦，明天少吃点'
        ]))
    elif food_analysis['has_carb'] and not (food_analysis['has_vegetable'] or food_analysis['has_fruit']):
        feedback_parts.append(random.choice([
            '碳水有点多，明天可以少一点',
            '主食吃多了，明天注意搭配蔬菜',
            '碳水化合物摄入偏高，明天调整一下'
        ]))
    elif food_analysis['is_healthy']:
        feedback_parts.append(random.choice([
            '饮食很健康，搭配得很不错',
            '今天吃得很均衡，继续保持',
            '蔬菜/水果充足，营养均衡'
        ]))
    elif food_analysis['has_protein']:
        feedback_parts.append(random.choice([
            '蛋白质摄入不错，继续保持',
            '蛋白质充足，对肌肉好',
            '有蛋白质，营养均衡'
        ]))

    if exercise and exercise_name:
        feedback_parts.append(random.choice([
            f'今天做了 {exercise_name} {exercise_duration} 分钟，很棒！',
            f'{exercise_name} {exercise_duration} 分钟，运动做得不错',
            f'坚持 {exercise_name} {exercise_duration} 分钟，继续保持'
        ]))
    elif exercise:
        feedback_parts.append(random.choice([
            '今天运动了，太棒了！',
            '运动做得好，继续坚持',
            '有运动习惯，身体会越来越好'
        ]))
    else:
        feedback_parts.append(random.choice([
            '明天记得运动哦',
            '运动可以帮助消耗，明天动起来',
            '建议明天安排一些运动'
        ]))

    return ' '.join(feedback_parts)


@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = UserService.get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('logout'))

    return render_template('index.html', user=user.to_dict())


@app.route('/login')
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/register')
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data.get('username')
    phone = data.get('phone')
    password = data.get('password')

    result = UserService.register(username, phone, password)

    if result['success']:
        session['user_id'] = result['user'].id
        return jsonify({'success': True, 'user': result['user'].to_dict()}), 201
    else:
        return jsonify({'success': False, 'message': result['message']}), 400


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')

    result = UserService.login(phone, password)

    if result['success']:
        session['user_id'] = result['user'].id
        return jsonify({'success': True, 'user': result['user'].to_dict()})
    else:
        return jsonify({'success': False, 'message': result['message']}), 401


@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.pop('user_id', None)
    return jsonify({'success': True})


@app.route('/api/auth/current-user')
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'user': None})

    user = UserService.get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'user': None})

    return jsonify({'user': user.to_dict()})


def require_login(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.route('/api/records', methods=['GET'])
@require_login
def get_all_records():
    records = RecordService.get_all_records(session['user_id'])
    return jsonify([r.to_dict(include_meals=True) for r in records])


@app.route('/api/records', methods=['POST'])
@require_login
def add_or_update_record():
    data = request.get_json()
    record_date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    record_date = datetime.strptime(record_date_str, '%Y-%m-%d').date()

    weight = data.get('weight')
    exercise = data.get('exercise', False)
    
    exercise_info = data.get('exercise_info', {}) or {}
    exercise_name = data.get('exercise_name') or (exercise_info.get('name') if exercise_info else None)
    exercise_duration = data.get('exercise_duration') or (exercise_info.get('duration') if exercise_info else None)
    
    hunger_data = data.get('hunger', {})
    hunger_times = data.get('hunger_times', 0) or hunger_data.get('times', 0)

    food_data = data.get('food', {})
    meals_data = data.get('meals', [])

    existing_record = RecordService.get_daily_record(session['user_id'], record_date)

    if existing_record:
        RecordService.update_daily_record(
            existing_record.id,
            session['user_id'],
            weight=weight,
            exercise=exercise,
            exercise_name=exercise_name,
            exercise_duration=exercise_duration,
            hunger_times=hunger_times
        )

        for meal_type in ['breakfast', 'lunch', 'dinner']:
            if meal_type not in food_data:
                continue
                
            meal_info = food_data[meal_type]
            recorded = meal_info.get('recorded', False)
            fullness = meal_info.get('fullness')
            description = meal_info.get('description')

            existing_meal = None
            for meal in existing_record.meals:
                if meal.meal_type == meal_type:
                    existing_meal = meal
                    break

            if recorded:
                if existing_meal:
                    RecordService.update_meal_record(
                        existing_meal.id,
                        fullness=fullness,
                        description=description
                    )
                else:
                    RecordService.add_meal_record(
                        existing_record.id,
                        meal_type,
                        fullness,
                        description
                    )
            elif existing_meal:
                RecordService.delete_meal_record(existing_meal.id)

        for meal_data in meals_data:
            meal_type = meal_data.get('meal_type')
            fullness = meal_data.get('fullness')
            description = meal_data.get('description')
            meal_id = meal_data.get('id')

            if meal_id:
                RecordService.update_meal_record(
                    meal_id,
                    fullness=fullness,
                    description=description
                )
            elif meal_data.get('recorded'):
                RecordService.add_meal_record(
                    existing_record.id,
                    meal_type,
                    fullness,
                    description
                )

        record = RecordService.get_daily_record_by_id(existing_record.id, session['user_id'])
    else:
        record = RecordService.create_daily_record(
            user_id=session['user_id'],
            record_date=record_date,
            weight=weight,
            exercise=exercise,
            exercise_name=exercise_name,
            exercise_duration=exercise_duration,
            hunger_times=hunger_times
        )

        for meal_type in ['breakfast', 'lunch', 'dinner']:
            meal_info = food_data.get(meal_type, {})
            if meal_info.get('recorded'):
                RecordService.add_meal_record(
                    record.id,
                    meal_type,
                    meal_info.get('fullness'),
                    meal_info.get('description')
                )

        for meal_data in meals_data:
            if meal_data.get('recorded'):
                RecordService.add_meal_record(
                    record.id,
                    meal_data.get('meal_type'),
                    meal_data.get('fullness'),
                    meal_data.get('description')
                )

    all_records = RecordService.get_all_records(session['user_id'])
    feedback = generate_feedback(record.to_dict(include_meals=True),
                                 [r.to_dict() for r in all_records])

    RecordService.update_daily_record(record.id, session['user_id'], feedback=feedback)
    record = RecordService.get_daily_record_by_id(record.id, session['user_id'])

    return jsonify(record.to_dict(include_meals=True)), 201


@app.route('/api/records/date/<date_str>', methods=['GET'])
@require_login
def get_record_by_date_api(date_str):
    record_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    record = RecordService.get_daily_record(session['user_id'], record_date)

    if record:
        return jsonify(record.to_dict(include_meals=True))
    return jsonify(None), 404


@app.route('/api/records/<int:record_id>', methods=['DELETE'])
@require_login
def delete_record(record_id):
    success = RecordService.delete_daily_record(record_id, session['user_id'])

    if success:
        return jsonify({'message': '记录已删除'}), 200
    return jsonify({'error': '删除失败'}), 400


@app.route('/api/records/<int:record_id>/meals/<meal_type>', methods=['DELETE'])
@require_login
def delete_meal_record(record_id, meal_type):
    record = RecordService.get_daily_record_by_id(record_id, session['user_id'])
    if not record:
        return jsonify({'error': '记录不存在'}), 404

    for meal in record.meals:
        if meal.meal_type == meal_type:
            RecordService.delete_meal_record(meal.id)
            return jsonify({'message': '餐食记录已删除'}), 200

    return jsonify({'error': '餐食记录不存在'}), 404


@app.route('/api/weight-trend', methods=['GET'])
@require_login
def get_weight_trend():
    records = RecordService.get_all_records(session['user_id'])
    records.sort(key=lambda x: x.record_date)
    trend = [{'date': r.record_date.isoformat(), 'weight': r.weight} for r in records if r.weight]
    return jsonify(trend)


@app.route('/api/records/latest')
@require_login
def get_latest_record():
    records = RecordService.get_all_records(session['user_id'], limit=1)
    if records:
        return jsonify(records[0].to_dict(include_meals=True))
    return jsonify(None), 404


@app.route('/api/migrate', methods=['POST'])
@require_login
def migrate_data():
    from migrate_to_db import migrate as do_migrate

    if 'user_id' not in session:
        return jsonify({'error': '请先登录'}), 401

    user = UserService.get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'error': '用户不存在'}), 400

    records_json = os.path.join(os.path.dirname(__file__), 'data', 'records.json')
    success = do_migrate(records_json, user.phone)

    if success:
        return jsonify({'message': '数据迁移成功'}), 200
    return jsonify({'error': '数据迁移失败'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
