from flask_wtf import FlaskForm
from wtforms import DateTimeField, StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

# ----- Вход (логин) -----
class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

# ----- Студент -----
class StudentForm(FlaskForm):
    full_name = StringField('ФИО студента', validators=[DataRequired(), Length(1, 128)])
    group_id = SelectField('Группа', coerce=int, validators=[Optional()])
    date_of_birth = DateField('Дата рождения', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Сохранить')

# ----- Группа -----
class GroupForm(FlaskForm):
    name = StringField('Название группы', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('Сохранить')

# ----- Консультация -----
class ConsultationForm(FlaskForm):
    date = DateTimeField(
        'Дата и время консультации',
        format='%Y-%m-%dT%H:%M',  # именно T для input type="datetime-local"
        validators=[DataRequired(message="Укажите дату и время консультации!")]
    )
    student_id = SelectField('Студент', coerce=int, validators=[DataRequired()])
    group_id = SelectField('Группа', coerce=int, validators=[Optional()])
    topic = StringField('Тема консультации', validators=[DataRequired(), Length(1, 255)])
    consultation_type = SelectField(
        'Тип консультации',
        choices=[
            ('Индивидуальная', 'Индивидуальная'),
            ('Групповая', 'Групповая'),
            ('Тестирование', 'Тестирование'),
        ],
        validators=[DataRequired()]
    )
    result = TextAreaField('Результаты/заметки', validators=[Optional(), Length(max=255)])
    psychologist = StringField('Психолог', validators=[Optional(), Length(1, 128)])
    submit = SubmitField('Сохранить')

# ----- Пользователь (создание/редактирование) -----
class UserForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Пароль', validators=[Optional()])
    full_name = StringField('ФИО', validators=[Optional(), Length(1, 128)])
    role = SelectField(
        'Роль',
        choices=[('admin', 'Администратор'), ('psychologist', 'Психолог')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Сохранить')

# ----- Кнопка поиска (универсальная форма для фильтрации) -----
class SearchForm(FlaskForm):
    query = StringField('Поиск', validators=[Optional()])
    submit = SubmitField('Искать')

