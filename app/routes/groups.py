from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import db, Group, Student
from app.forms import GroupForm

groups_bp = Blueprint('groups', __name__, url_prefix='/groups')

# ----------- Список групп -----------
@groups_bp.route('/')
@login_required
def list_groups():
    groups = Group.query.all()
    return render_template('groups/list.html', groups=groups)

# ----------- Добавить группу -----------
@groups_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_group():
    form = GroupForm()
    if form.validate_on_submit():
        if Group.query.filter_by(name=form.name.data).first():
            flash('Такая группа уже есть!', 'warning')
            return redirect(url_for('groups.list_groups'))
        group = Group(name=form.name.data)
        db.session.add(group)
        db.session.commit()
        flash('Группа добавлена.', 'success')
        return redirect(url_for('groups.list_groups'))
    return render_template('groups/add_edit.html', form=form, edit=False)

# ----------- Редактировать группу -----------
@groups_bp.route('/edit/<int:group_id>', methods=['GET', 'POST'])
@login_required
def edit_group(group_id):
    group = Group.query.get_or_404(group_id)
    form = GroupForm(obj=group)
    if form.validate_on_submit():
        group.name = form.name.data
        db.session.commit()
        flash('Название группы обновлено.', 'success')
        return redirect(url_for('groups.list_groups'))
    return render_template('groups/add_edit.html', form=form, edit=True, group=group)

# ----------- Удалить группу -----------
@groups_bp.route('/delete/<int:group_id>', methods=['POST'])
@login_required
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    # Перед удалением убираем у студентов эту группу
    for s in group.students:
        s.group_id = None
    db.session.delete(group)
    db.session.commit()
    flash('Группа удалена.', 'success')
    return redirect(url_for('groups.list_groups'))

# ----------- Студенты в группе -----------
@groups_bp.route('/<int:group_id>/students')
@login_required
def group_students(group_id):
    group = Group.query.get_or_404(group_id)
    students = Student.query.filter_by(group_id=group_id).all()
    return render_template('students/list.html', groups=[group], students=students, selected_group=group_id)
