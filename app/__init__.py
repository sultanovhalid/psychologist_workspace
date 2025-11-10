from flask import Flask
from flask_login import LoginManager
from app.models import db, User, init_db

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    # Инициализация SQLAlchemy
    db.init_app(app)

    # Инициализация БД и наполнение тестовыми данными
    with app.app_context():
        init_db(app)

    # Flask-Login
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Пожалуйста, войдите в систему."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Регистрация блюпринтов
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.analytics import analytics_bp
    from app.routes.students import students_bp
    from app.routes.groups import groups_bp
    from app.routes.consultations import consultations_bp
    from app.routes.backup import backup_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(consultations_bp)
    app.register_blueprint(backup_bp)

    # Главная страница
    @app.route('/')
    def index():
        from flask_login import current_user
        if not current_user.is_authenticated:
            return app.send_static_file('index.html') if app.has_static_folder else "Привет!"
        # Подсчёты для дашборда
        from app.models import Student, Group, Consultation
        stats = {
            'students': Student.query.count(),
            'groups': Group.query.count(),
            'consultations': Consultation.query.count(),
        }
        recent_consultations = Consultation.query.order_by(Consultation.date.desc()).limit(7).all()
        return app.render_template('dashboard.html', stats=stats, recent_consultations=recent_consultations)

    return app
