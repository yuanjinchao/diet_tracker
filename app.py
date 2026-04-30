from flask import Flask, render_template, request, jsonify
import json
import os
import random
from datetime import datetime

app = Flask(__name__)

DATA_FILE = 'data/records.json'

def init_data_file():
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)

def get_records():
    init_data_file()
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_record(record):
    records = get_records()
    records.append(record)
    with open(DATA_FILE, 'w') as f:
        json.dump(records, f, indent=2)

def update_record(record_id, updated_data):
    records = get_records()
    for i, record in enumerate(records):
        if record['id'] == record_id:
            records[i] = {**record, **updated_data}
            with open(DATA_FILE, 'w') as f:
                json.dump(records, f, indent=2)
            return records[i]
    return None

def get_record_by_date(date_str):
    records = get_records()
    for record in records:
        if record['date'].startswith(date_str):
            return record
    return None

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

def generate_feedback(weight, food, exercise, exercise_info=None, fullness_data=None, hunger_data=None):
    records = get_records()
    feedback_parts = []
    
    if len(records) >= 1:
        prev_weight = records[-1]['weight']
        weight_change = weight - prev_weight
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
            '开始记录第一天，加油！',
            '第一天记录，希望你坚持下去',
            '新的开始，祝你成功'
        ]))
    
    if fullness_data:
        avg_fullness = sum(fullness_data.values()) / len(fullness_data)
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
    
    if hunger_data and hunger_data.get('times', 0) > 0:
        hunger_times = hunger_data['times']
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
    
    food_analysis = analyze_food(food)
    
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
    
    if exercise and exercise_info:
        exercise_name = exercise_info.get('name', '运动')
        duration = exercise_info.get('duration', 30)
        feedback_parts.append(random.choice([
            f'今天做了 {exercise_name} {duration} 分钟，很棒！',
            f'{exercise_name} {duration} 分钟，运动做得不错',
            f'坚持 {exercise_name} {duration} 分钟，继续保持'
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
    return render_template('index.html')

@app.route('/api/records', methods=['GET'])
def get_all_records():
    records = get_records()
    records.sort(key=lambda x: x['date'], reverse=True)
    return jsonify(records)

@app.route('/api/records', methods=['POST'])
def add_record():
    data = request.get_json()
    weight = float(data['weight']) if data.get('weight') else None
    food = data.get('food', '')
    exercise = data.get('exercise', False)
    exercise_info = data.get('exercise_info', None)
    fullness_data = data.get('fullness', {})
    hunger_data = data.get('hunger', {})
    record_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    existing_record = get_record_by_date(record_date)
    
    if existing_record:
        # 判断是否是全天打卡（包含三餐）
        is_full_day = all(key in fullness_data for key in ['breakfast', 'lunch', 'dinner'])
        
        updated_data = {}
        if weight is not None:
            updated_data['weight'] = weight
        if food:
            if is_full_day:
                # 全天打卡：覆盖食物信息
                updated_data['food'] = food
            else:
                # 单餐打卡：追加食物信息
                combined_food = existing_record.get('food', '') + ' | ' + food if existing_record.get('food') else food
                updated_data['food'] = combined_food
        updated_data['exercise'] = exercise
        if exercise_info:
            updated_data['exercise_info'] = exercise_info
        if fullness_data:
            if is_full_day:
                # 全天打卡：覆盖饱腹感
                updated_data['fullness'] = fullness_data
            else:
                # 单餐打卡：合并饱腹感
                updated_data['fullness'] = {**existing_record.get('fullness', {}), **fullness_data}
        if hunger_data:
            updated_data['hunger'] = hunger_data
        
        updated_record = update_record(existing_record['id'], updated_data)
        if updated_record:
            updated_record['feedback'] = generate_feedback(
                updated_record.get('weight') or 70,
                updated_record.get('food', ''),
                updated_record.get('exercise', False),
                updated_record.get('exercise_info'),
                updated_record.get('fullness', {}),
                updated_record.get('hunger', {})
            )
            update_record(existing_record['id'], {'feedback': updated_record['feedback']})
            return jsonify(updated_record), 200
        return jsonify({'error': '更新失败'}), 500
    
    record = {
        'id': len(get_records()) + 1,
        'date': record_date + ' ' + datetime.now().strftime('%H:%M:%S'),
        'weight': weight,
        'food': food,
        'exercise': exercise,
        'exercise_info': exercise_info,
        'fullness': fullness_data,
        'hunger': hunger_data,
        'feedback': generate_feedback(weight or 70, food, exercise, exercise_info, fullness_data, hunger_data) if (weight or food or exercise) else ''
    }
    
    save_record(record)
    return jsonify(record), 201

@app.route('/api/records/date/<date_str>', methods=['GET'])
def get_record_by_date_api(date_str):
    record = get_record_by_date(date_str)
    if record:
        return jsonify(record)
    return jsonify(None), 404

@app.route('/api/weight-trend', methods=['GET'])
def get_weight_trend():
    records = get_records()
    records.sort(key=lambda x: x['date'])
    trend = [{'date': r['date'][:10], 'weight': r['weight']} for r in records]
    return jsonify(trend)

@app.route('/api/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    records = get_records()
    records = [r for r in records if r['id'] != record_id]
    
    with open(DATA_FILE, 'w') as f:
        json.dump(records, f, indent=2)
    
    return jsonify({'message': '记录已删除'}), 200

if __name__ == '__main__':
    app.run(debug=True)
