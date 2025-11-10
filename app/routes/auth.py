from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User
from app.forms import LoginForm, UserForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ---- Вход ----
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # Исправлено
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Вы успешно вошли.', 'success')
            return redirect(url_for('index'))  # Исправлено
        else:
            flash('Неверный логин или пароль.', 'danger')
    return render_template('login.html', form=form)

# ---- Выход ----
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('auth.login'))

# ---- (Опционально) Регистрация пользователя через форму ----
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Логин уже занят!', 'warning')
            return render_template('register.html', form=form)
        user = User(
            username=form.username.data,
            full_name=form.full_name.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Пользователь зарегистрирован. Теперь войдите.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)
