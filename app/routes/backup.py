import os
import shutil
from flask import Blueprint, render_template, flash, redirect, url_for, send_file, current_app, request
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
from app.models import db

backup_bp = Blueprint('backup', __name__, url_prefix='/backup')

# Декоратор для проверки роли "админ"
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Требуются права администратора.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@backup_bp.route('/')
@login_required
@admin_required
def backup_page():
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    backup_dir = os.path.join(os.path.dirname(db_path), "backups")
    is_dir = os.path.isdir(backup_dir)
    backups = []
    if is_dir:
        # Список файлов-бекапов, отсортированных по дате изменения (от новых к старым)
        backups = sorted(
            [f for f in os.listdir(backup_dir) if f.endswith('.sqlite')],
            key=lambda f: os.path.getmtime(os.path.join(backup_dir, f)),
            reverse=True
        )
    return render_template(
        'settings/backup.html',
        backup_dir=backup_dir,
        is_dir=is_dir,
        backups=backups
    )

@backup_bp.route('/make', methods=['POST'])
@login_required
@admin_required
def make_backup():
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.exists(db_path):
        flash('База данных не найдена.', 'danger')
        return redirect(url_for('backup.backup_page'))

    backup_dir = os.path.join(os.path.dirname(db_path), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f"backup_{now_str}.sqlite")

    try:
        import shutil
        shutil.copyfile(db_path, backup_file)
        flash(f'Бэкап успешно создан: {os.path.basename(backup_file)}', 'success')
    except Exception as e:
        flash(f'Ошибка при создании бэкапа: {e}', 'danger')
    return redirect(url_for('backup.backup_page'))

@backup_bp.route('/download/<filename>')
@login_required
@admin_required
def download_backup(filename):
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    backup_dir = os.path.join(os.path.dirname(db_path), "backups")
    file_path = os.path.join(backup_dir, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    flash('Файл не найден.', 'danger')
    return redirect(url_for('backup.backup_page'))

@backup_bp.route('/restore', methods=['POST'])
@login_required
@admin_required
def restore_backup():
    db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
    if not db_uri.startswith('sqlite:///'):
        flash('Восстановление поддерживается только для SQLite.', 'danger')
        return redirect(url_for('backup.backup_page'))

    uploaded = request.files.get('backup_file')
    if not uploaded or not uploaded.filename:
        flash('Выберите файл .sqlite для восстановления.', 'warning')
        return redirect(url_for('backup.backup_page'))

    filename = secure_filename(uploaded.filename)
    if not filename.lower().endswith('.sqlite'):
        flash('Разрешены только файлы .sqlite.', 'danger')
        return redirect(url_for('backup.backup_page'))

    db_path = db_uri.replace('sqlite:///', '')
    backup_dir = os.path.join(os.path.dirname(db_path), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    temp_path = os.path.join(backup_dir, f"upload_{now_str}.sqlite")
    pre_restore = os.path.join(backup_dir, f"pre_restore_{now_str}.sqlite")

    try:
        uploaded.save(temp_path)
        if os.path.exists(db_path):
            shutil.copyfile(db_path, pre_restore)
        db.session.remove()
        try:
            db.engine.dispose()
        except Exception:
            pass
        shutil.copyfile(temp_path, db_path)
        flash('База данных восстановлена. Создана копия до восстановления.', 'success')
    except Exception as e:
        flash(f'Ошибка при восстановлении: {e}', 'danger')
    finally:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass
    return redirect(url_for('backup.backup_page'))
