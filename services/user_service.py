from models import db, User
from datetime import datetime


class UserService:
    @staticmethod
    def register(username, phone, password):
        if not phone.isdigit() or len(phone) != 11 or not phone.startswith('1'):
            return {'success': False, 'message': '请输入正确的11位手机号'}

        if User.query.filter_by(phone=phone).first():
            return {'success': False, 'message': '该手机号已被注册'}

        if User.query.filter_by(username=username).first():
            return {'success': False, 'message': '该用户名已被使用'}

        user = User(
            username=username,
            phone=phone,
            password=password,
            create_time=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()

        return {'success': True, 'user': user}

    @staticmethod
    def login(phone, password):
        user = User.query.filter_by(phone=phone, password=password).first()

        if not user:
            return {'success': False, 'message': '手机号或密码错误'}

        return {'success': True, 'user': user}

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_phone(phone):
        return User.query.filter_by(phone=phone).first()
