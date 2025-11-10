from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# =====================
# User (Пользователи)
# =====================
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(16), nullable=False, default='psychologist')  # 'psychologist' or 'admin'
    full_name = db.Column(db.String(128), nullable=True)

    def set_password(self, password):
        self.password_hash = password  # Без хеширования

    def check_password(self, password):
        return self.password_hash == password  # Просто сравнение

# =====================
# Group (Группы)
# =====================
class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    students = db.relationship('Student', backref='group', lazy=True)

# =====================
# Student (Студенты)
# =====================
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(128), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)

    consultations = db.relationship('Consultation', backref='student', lazy=True)

# =====================
# Consultation (Консультации)
# =====================
class Consultation(db.Model):
    __tablename__ = 'consultations'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)

    topic = db.Column(db.String(255), nullable=False)
    consultation_type = db.Column(db.String(64), nullable=False)   # индивидуальная, групповая, тестирование и др.
    result = db.Column(db.String(255), nullable=True)
    psychologist = db.Column(db.String(128), nullable=True)        # ФИО психолога

# =====================
# Log (Журнал действий)
# =====================
class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# =====================
# Автоинициализация и заполнение БД тестовыми данными
# =====================
def init_db(app):
    with app.app_context():
        db.create_all()

        # Заполняем, если пусто
        if not User.query.first():
            admin = User(username='admin', full_name='Администратор', role='admin')
            admin.set_password('admin')
            psy = User(username='psych', full_name='Психолог Иванова И.И.', role='psychologist')
            psy.set_password('psych')
            db.session.add_all([admin, psy])
            db.session.commit()

        if not Group.query.first():
            g1 = Group(name='1-ИТ')
            g2 = Group(name='2-Эконом')
            db.session.add_all([g1, g2])
            db.session.commit()

        if not Student.query.first():
            s1 = Student(full_name='Иванов Сергей Петрович', group_id=1)
            s2 = Student(full_name='Петрова Мария Николаевна', group_id=2)
            s3 = Student(full_name='Сидорова Анна Александровна', group_id=1)
            db.session.add_all([s1, s2, s3])
            db.session.commit()

        if not Consultation.query.first():
            c1 = Consultation(
                date=datetime(2024, 6, 1, 10, 0),
                student_id=1,
                group_id=1,
                topic="Профориентация",
                consultation_type="Индивидуальная",
                result="Дано направление на дополнительное тестирование.",
                psychologist="Психолог Иванова И.И."
            )
            c2 = Consultation(
                date=datetime(2024, 6, 2, 12, 0),
                student_id=2,
                group_id=2,
                topic="Диагностика стресса",
                consultation_type="Групповая",
                result="Проведена диагностика. Даны рекомендации.",
                psychologist="Психолог Иванова И.И."
            )
            db.session.add_all([c1, c2])
            db.session.commit()
