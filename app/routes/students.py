from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import db, Student, Group
from app.forms import StudentForm, SearchForm

students_bp = Blueprint('students', __name__, url_prefix='/students')

# ----------- Список студентов -----------
@students_bp.route('/', methods=['GET', 'POST'])
@login_required
def list_students():
    form = SearchForm()
    group_id = request.args.get('group_id', type=int)
    query = Student.query
    if group_id:
        query = query.filter_by(group_id=group_id)
    search = form.query.data if form.validate_on_submit() else request.args.get('query', '')
    if search:
        query = query.filter(Student.full_name.ilike(f"%{search}%"))
    students = query.order_by(Student.full_name).all()
    groups = Group.query.all()
    return render_template('students/list.html', students=students, groups=groups, form=form, group_id=group_id, search=search)

# ----------- Добавить студента -----------
@students_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_student():
    form = StudentForm()
    groups = Group.query.all()
    form.group_id.choices = [(0, '-')] + [(g.id, g.name) for g in groups]
    if form.validate_on_submit():
        student = Student(
            full_name=form.full_name.data,
            group_id=form.group_id.data if form.group_id.data else None,
            date_of_birth=form.date_of_birth.data
        )
        db.session.add(student)
        db.session.commit()
        flash('Студент добавлен.', 'success')
        return redirect(url_for('students.list_students'))
    return render_template('students/add_edit.html', form=form, edit=False)

# ----------- Редактировать студента -----------
@students_bp.route('/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    form = StudentForm(obj=student)
    groups = Group.query.all()
    form.group_id.choices = [(0, '-')] + [(g.id, g.name) for g in groups]
    if form.validate_on_submit():
        student.full_name = form.full_name.data
        student.group_id = form.group_id.data if form.group_id.data else None
        student.date_of_birth = form.date_of_birth.data
        db.session.commit()
        flash('Данные студента обновлены.', 'success')
        return redirect(url_for('students.list_students'))
    return render_template('students/add_edit.html', form=form, edit=True)

# ----------- Удалить студента -----------
@students_bp.route('/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Студент удалён.', 'success')
    return redirect(url_for('students.list_students'))
