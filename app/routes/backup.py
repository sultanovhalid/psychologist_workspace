import os
from flask import Blueprint, render_template, flash, redirect, url_for, send_file, current_app
from flask_login import login_required, current_user
from datetime import datetime

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
    return render_template('settings/backup.html')

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
