from flask import Flask, render_template
from flask_login import LoginManager
from app.models import db, User, init_db


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    # Инициализация SQLAlchemy (ТОЛЬКО ОДИН РАЗ)
    db.init_app(app)

    # Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Пожалуйста, войдите в систему."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Регистрация блюпринтов — после init_app инициализации!
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.analytics import analytics_bp
    from app.routes.students import students_bp
    from app.routes.groups import groups_bp
    from app.routes.consultations import consultations_bp
    from app.routes.backup import backup_bp

    # новые блюпринты
    from app.routes.consultation_topics import consultation_topics_bp
    from app.routes.group_events import group_events_bp
    from app.routes.diagnostics import diagnostics_bp
    from app.routes.risk_groups import risk_groups_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(consultations_bp)
    app.register_blueprint(backup_bp)

    # регистрация новых
    app.register_blueprint(consultation_topics_bp)
    app.register_blueprint(group_events_bp)
    app.register_blueprint(diagnostics_bp)
    app.register_blueprint(risk_groups_bp)

    # Главная страница
    @app.route('/')
    def index():
        from flask_login import current_user
        from app.models import Student, Group, Consultation
        if not current_user.is_authenticated:
            return render_template('index.html')
        stats = {
            'students': Student.query.count(),
            'groups': Group.query.count(),
            'consultations': Consultation.query.count(),
        }
        recent_consultations = (
            Consultation.query
            .order_by(Consultation.date.desc())
            .limit(7)
            .all()
        )
        return render_template(
            'dashboard.html',
            stats=stats,
            recent_consultations=recent_consultations
        )

    # Создание БД и наполнение тестовыми данными
    with app.app_context():
        init_db(app)

    return app
