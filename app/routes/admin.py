from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, User, Log
from app.forms import UserForm
from werkzeug.security import generate_password_hash
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

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

# ----------- Управление пользователями -----------
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Логин уже занят!', 'warning')
            return render_template('admin/users.html', users=User.query.all())
        user = User(
            username=form.username.data,
            full_name=form.full_name.data,
            role=form.role.data,
        )
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        else:
            user.password_hash = generate_password_hash('defaultpass')
        db.session.add(user)
        db.session.commit()
        flash('Пользователь добавлен.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/users.html', users=User.query.all(), form=form)

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.full_name = form.full_name.data
        user.role = form.role.data
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Данные пользователя обновлены.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/users.html', users=User.query.all(), form=form, edit_id=user_id)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь удалён.', 'success')
    return redirect(url_for('admin.users'))

# ----------- Просмотр логов -----------
@admin_bp.route('/logs')
@login_required
@admin_required
def logs():
    logs = Log.query.order_by(Log.timestamp.desc()).limit(500).all()
    return render_template('admin/logs.html', logs=logs)
