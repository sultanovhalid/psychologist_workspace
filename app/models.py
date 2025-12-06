from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from flask_login import UserMixin

db = SQLAlchemy()

# =====================
# User (Пользователи)
# =====================
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(16), nullable=False, default='psychologist')  # 'psychologist' or 'admin'
    full_name = db.Column(db.String(128), nullable=True)

    # Связи с новыми сущностями
    group_events = db.relationship('GroupEvent', backref='psychologist_user', lazy=True)
    test_results = db.relationship('TestResult', backref='psychologist_user', lazy=True)

    def set_password(self, password):
        # В учебных целях без хеширования (для реальных систем требуется хеширование)
        self.password_hash = password

    def check_password(self, password):
        return self.password_hash == password


# =====================
# Group (Группы)
# =====================
class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    students = db.relationship('Student', backref='group', lazy=True)
    # Новая связь: мероприятия с группой
    events = db.relationship('GroupEvent', backref='group', lazy=True)


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

    # Новые связи: результаты тестов и учёт в группе риска
    test_results = db.relationship('TestResult', backref='student', lazy=True)
    risk_records = db.relationship('RiskGroup', backref='student', lazy=True)


# =====================
# ConsultationTopic (Справочник тематик консультаций)
# =====================
class ConsultationTopic(db.Model):
    __tablename__ = 'consultation_topics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # Обратная связь: консультации по данной тематике
    consultations = db.relationship('Consultation', backref='topic_ref', lazy=True)


# =====================
# Consultation (Консультации)
# =====================
class Consultation(db.Model):
    __tablename__ = 'consultations'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)

    # Новый FK на справочник тематик (НЕ ломает существующий экспорт)
    topic_id = db.Column(db.Integer, db.ForeignKey('consultation_topics.id'), nullable=True)

    topic = db.Column(db.String(255), nullable=False)           # старое текстовое поле — остаётся для CSV/1С
    consultation_type = db.Column(db.String(64), nullable=False)  # индивидуальная, групповая, тестирование и др.
    result = db.Column(db.String(255), nullable=True)
    psychologist = db.Column(db.String(128), nullable=True)     # ФИО психолога


# =====================
# GroupEvent (Групповые мероприятия)
# =====================
class GroupEvent(db.Model):
    __tablename__ = 'group_events'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    title = db.Column(db.String(255), nullable=False)           # тема/название мероприятия
    event_type = db.Column(db.String(64), nullable=False)       # тренинг, лекция, классный час, род. собрание и т.п.

    psychologist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    participants_count = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(255), nullable=True)


# =====================
# PsychologicalTest (Справочник психодиагностических методик)
# =====================
class PsychologicalTest(db.Model):
    __tablename__ = 'psychological_tests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)       # полное название методики
    short_name = db.Column(db.String(64), nullable=True)                # краткое название / аббревиатура
    description = db.Column(db.String(255), nullable=True)              # что измеряет
    target_group = db.Column(db.String(128), nullable=True)             # для кого (1 курс, родители и т.п.)

    test_results = db.relationship('TestResult', backref='test', lazy=True)


# =====================
# TestResult (Результаты психодиагностики)
# =====================
class TestResult(db.Model):
    __tablename__ = 'test_results'
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('psychological_tests.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    raw_score = db.Column(db.String(64), nullable=True)         # первичный балл, можно хранить строкой
    level = db.Column(db.String(64), nullable=True)             # интерпретация: низкий/средний/высокий и т.п.
    comment = db.Column(db.String(255), nullable=True)

    psychologist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)


# =====================
# RiskGroup (Учёт студентов «группы риска»)
# =====================
class RiskGroup(db.Model):
    __tablename__ = 'risk_groups'
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date_added = db.Column(db.Date, nullable=False, default=date.today)

    risk_level = db.Column(db.String(32), nullable=False, default='средний')  # низкий/средний/высокий и т.п.
    reason = db.Column(db.String(255), nullable=True)

    status = db.Column(db.String(32), nullable=False, default='активен')      # активен / снят
    date_removed = db.Column(db.Date, nullable=True)


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

        # Пользователи
        if not User.query.first():
            admin = User(username='admin', full_name='Администратор', role='admin')
            admin.set_password('admin')

            psy = User(username='psych', full_name='Психолог Иванова И.И.', role='psychologist')
            psy.set_password('psych')

            db.session.add_all([admin, psy])
            db.session.commit()

        # Группы
        if not Group.query.first():
            g1 = Group(name='1-ИТ')
            g2 = Group(name='2-Эконом')
            db.session.add_all([g1, g2])
            db.session.commit()

        # Студенты
        if not Student.query.first():
            s1 = Student(full_name='Иванов Сергей Петрович', group_id=1)
            s2 = Student(full_name='Петрова Мария Николаевна', group_id=2)
            s3 = Student(full_name='Сидорова Анна Александровна', group_id=1)
            db.session.add_all([s1, s2, s3])
            db.session.commit()

        # Справочник тематик консультаций
        if not ConsultationTopic.query.first():
            t1 = ConsultationTopic(
                name='Профориентация',
                description='Выбор профессии, планирование образовательного маршрута.'
            )
            t2 = ConsultationTopic(
                name='Учебная мотивация',
                description='Трудности обучения, снижение интереса к учебе.'
            )
            t3 = ConsultationTopic(
                name='Личностные и эмоциональные трудности',
                description='Стресс, тревога, конфликты, самооценка.'
            )
            db.session.add_all([t1, t2, t3])
            db.session.commit()

        # Консультации
        if not Consultation.query.first():
            c1 = Consultation(
                date=datetime(2024, 6, 1, 10, 0),
                student_id=1,
                group_id=1,
                topic_id=1,  # Профориентация
                topic="Профориентация",
                consultation_type="Индивидуальная",
                result="Дано направление на дополнительное тестирование.",
                psychologist="Психолог Иванова И.И."
            )
            c2 = Consultation(
                date=datetime(2024, 6, 2, 12, 0),
                student_id=2,
                group_id=2,
                topic_id=3,  # Личностные и эмоциональные трудности
                topic="Диагностика стресса",
                consultation_type="Групповая",
                result="Проведена диагностика. Даны рекомендации.",
                psychologist="Психолог Иванова И.И."
            )
            db.session.add_all([c1, c2])
            db.session.commit()

        # Справочник психодиагностических методик
        if not PsychologicalTest.query.first():
            test1 = PsychologicalTest(
                name='Шкала реактивной и личностной тревожности Спилбергера–Ханина',
                short_name='СТАИ',
                description='Оценка уровня тревожности.',
                target_group='Студенты 1–4 курсов'
            )
            test2 = PsychologicalTest(
                name='Методика диагностики уровня школьной мотивации',
                short_name='Мотивация обучения',
                description='Оценка учебной мотивации.',
                target_group='Студенты 1 курса'
            )
            db.session.add_all([test1, test2])
            db.session.commit()

        # Пример результатов тестирования
        if not TestResult.query.first():
            tr1 = TestResult(
                student_id=1,
                test_id=1,
                date=datetime(2024, 6, 3, 11, 0),
                raw_score='45',
                level='Умеренно повышенный уровень тревожности',
                comment='Рекомендовано индивидуальное консультирование.',
                psychologist_id=2  # psych
            )
            tr2 = TestResult(
                student_id=2,
                test_id=2,
                date=datetime(2024, 6, 4, 9, 30),
                raw_score='18',
                level='Средний уровень учебной мотивации',
                comment='Рекомендована работа по развитию учебной мотивации.',
                psychologist_id=2
            )
            db.session.add_all([tr1, tr2])
            db.session.commit()

        # Пример учёта «группы риска»
        if not RiskGroup.query.first():
            rg1 = RiskGroup(
                student_id=1,
                date_added=date(2024, 6, 5),
                risk_level='высокий',
                reason='Частые пропуски занятий, высокий уровень тревожности.',
                status='активен'
            )
            rg2 = RiskGroup(
                student_id=3,
                date_added=date(2024, 6, 6),
                risk_level='средний',
                reason='Конфликты в группе, снижение успеваемости.',
                status='активен'
            )
            db.session.add_all([rg1, rg2])
            db.session.commit()

        # Пример групповых мероприятий
        if not GroupEvent.query.first():
            ge1 = GroupEvent(
                date=datetime(2024, 6, 7, 13, 0),
                group_id=1,
                title='Тренинг по развитию коммуникации в группе',
                event_type='Тренинг',
                psychologist_id=2,
                participants_count=15,
                description='Групповое упражнение на сплочение и навыки общения.'
            )
            ge2 = GroupEvent(
                date=datetime(2024, 6, 8, 15, 0),
                group_id=2,
                title='Профориентационная лекция',
                event_type='Лекция',
                psychologist_id=2,
                participants_count=20,
                description='Обзор востребованных профессий и образовательных траекторий.'
            )
            db.session.add_all([ge1, ge2])
            db.session.commit()
