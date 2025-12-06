from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    SelectField,
    DateField,
    DateTimeField,
    TextAreaField,
    HiddenField,
    BooleanField,
    IntegerField,
)
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
    date = DateTimeField('Дата и время консультации', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
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


# ==========================
# НОВЫЕ ФОРМЫ
# ==========================

# ----- Тематика консультации (справочник ConsultationTopic) -----
class ConsultationTopicForm(FlaskForm):
    name = StringField('Название тематики', validators=[DataRequired(), Length(1, 128)])
    description = TextAreaField('Описание', validators=[Optional(), Length(max=255)])
    is_active = BooleanField('Активна', default=True)
    submit = SubmitField('Сохранить')


# ----- Групповое мероприятие (GroupEvent) -----
class GroupEventForm(FlaskForm):
    date = DateTimeField(
        'Дата и время мероприятия',
        format='%Y-%m-%d %H:%M',
        validators=[DataRequired()]
    )
    group_id = SelectField('Группа', coerce=int, validators=[Optional()])
    title = StringField('Тема / название мероприятия', validators=[DataRequired(), Length(1, 255)])
    event_type = SelectField(
        'Тип мероприятия',
        choices=[
            ('Тренинг', 'Тренинг'),
            ('Лекция', 'Лекция'),
            ('Классный час', 'Классный час'),
            ('Родительское собрание', 'Родительское собрание'),
            ('Другое', 'Другое'),
        ],
        validators=[DataRequired()]
    )
    psychologist_id = SelectField('Психолог', coerce=int, validators=[Optional()])
    participants_count = IntegerField('Количество участников', validators=[Optional()])
    description = TextAreaField('Краткое описание / примечания', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Сохранить')


# ----- Психодиагностическая методика (PsychologicalTest) -----
class PsychologicalTestForm(FlaskForm):
    name = StringField('Название методики', validators=[DataRequired(), Length(1, 255)])
    short_name = StringField('Краткое название / аббревиатура', validators=[Optional(), Length(max=64)])
    description = TextAreaField('Описание (что измеряет)', validators=[Optional(), Length(max=255)])
    target_group = StringField('Целевая группа (курс, категория)', validators=[Optional(), Length(max=128)])
    submit = SubmitField('Сохранить')


# ----- Результат тестирования (TestResult) -----
class TestResultForm(FlaskForm):
    date = DateTimeField(
        'Дата и время тестирования',
        format='%Y-%m-%d %H:%M',
        validators=[DataRequired()]
    )
    student_id = SelectField('Студент', coerce=int, validators=[DataRequired()])
    test_id = SelectField('Методика', coerce=int, validators=[DataRequired()])
    raw_score = StringField('Первичный балл / результат', validators=[Optional(), Length(max=64)])
    level = StringField('Уровень / интерпретация', validators=[Optional(), Length(max=64)])
    comment = TextAreaField('Комментарий психолога', validators=[Optional(), Length(max=255)])
    psychologist_id = SelectField('Психолог', coerce=int, validators=[Optional()])
    submit = SubmitField('Сохранить')


# ----- Учёт «группы риска» (RiskGroup) -----
class RiskGroupForm(FlaskForm):
    student_id = SelectField('Студент', coerce=int, validators=[DataRequired()])
    date_added = DateField(
        'Дата постановки в группу риска',
        format='%Y-%m-%d',
        validators=[DataRequired()]
    )
    risk_level = SelectField(
        'Уровень риска',
        choices=[
            ('низкий', 'Низкий'),
            ('средний', 'Средний'),
            ('высокий', 'Высокий'),
        ],
        validators=[DataRequired()]
    )
    reason = TextAreaField('Причина включения', validators=[Optional(), Length(max=255)])
    status = SelectField(
        'Статус',
        choices=[
            ('активен', 'Активен'),
            ('снят', 'Снят с учета'),
        ],
        validators=[DataRequired()]
    )
    date_removed = DateField(
        'Дата снятия с учета',
        format='%Y-%m-%d',
        validators=[Optional()]
    )
    submit = SubmitField('Сохранить')
