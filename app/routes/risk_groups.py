from datetime import date

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required

from app.models import db, RiskGroup, Student, Group
from app.forms import RiskGroupForm

risk_groups_bp = Blueprint(
    'risk_groups',
    __name__,
    url_prefix='/risk_groups'
)


# ==========================
# Вспомогательная функция
# ==========================

def _populate_risk_form_choices(form: RiskGroupForm):
    """Заполняем список студентов для формы учёта группы риска."""
    students = (
        Student.query
        .order_by(Student.full_name.asc())
        .all()
    )
    form.student_id.choices = [(s.id, s.full_name) for s in students]


# ==========================
# Список студентов «группы риска»
# ==========================

@risk_groups_bp.route('/', methods=['GET'])
@login_required
def list_risk():
    """
    Список записей «группы риска».
    Поддерживаются фильтры:
      - по группе (group_id)
      - по уровню риска (risk_level)
      - по статусу (status)
    """
    group_id = request.args.get('group_id', type=int)
    risk_level = request.args.get('risk_level', type=str)
    status = request.args.get('status', type=str)

    # Базовый запрос с присоединением студента и группы
    query = (
        RiskGroup.query
        .join(Student, RiskGroup.student_id == Student.id)
        .outerjoin(Group, Student.group_id == Group.id)
    )

    if group_id:
        query = query.filter(Student.group_id == group_id)

    if risk_level:
        query = query.filter(RiskGroup.risk_level == risk_level)

    if status:
        query = query.filter(RiskGroup.status == status)

    risk_records = (
        query
        .order_by(RiskGroup.status.desc(), RiskGroup.risk_level.desc(), RiskGroup.date_added.desc())
        .all()
    )

    groups = Group.query.order_by(Group.name.asc()).all()

    # Для фильтров по уровню риска и статусу вытаскиваем уникальные значения
    risk_levels = (
        db.session.query(RiskGroup.risk_level)
        .distinct()
        .order_by(RiskGroup.risk_level.asc())
        .all()
    )
    risk_levels = [rl[0] for rl in risk_levels]

    statuses = (
        db.session.query(RiskGroup.status)
        .distinct()
        .order_by(RiskGroup.status.asc())
        .all()
    )
    statuses = [st[0] for st in statuses]

    return render_template(
        'risk_groups/list.html',
        risk_records=risk_records,
        groups=groups,
        risk_levels=risk_levels,
        statuses=statuses,
        selected_group_id=group_id,
        selected_risk_level=risk_level,
        selected_status=status,
    )


# ==========================
# Постановка в «группу риска»
# ==========================

@risk_groups_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_risk():
    """
    Создание записи о включении студента в «группу риска».
    """
    form = RiskGroupForm()
    _populate_risk_form_choices(form)

    # Значения по умолчанию
    if request.method == 'GET':
        if not form.date_added.data:
            form.date_added.data = date.today()
        if not form.status.data:
            form.status.data = 'активен'

    if form.validate_on_submit():
        record = RiskGroup(
            student_id=form.student_id.data,
            date_added=form.date_added.data,
            risk_level=form.risk_level.data,
            reason=form.reason.data.strip() if form.reason.data else None,
            status=form.status.data,
            date_removed=form.date_removed.data if form.date_removed.data else None,
        )
        db.session.add(record)
        db.session.commit()
        flash('Студент поставлен в «группу риска».', 'success')
        return redirect(url_for('risk_groups.list_risk'))

    return render_template(
        'risk_groups/form.html',
        form=form,
        title='Постановка в «группу риска»',
    )


# ==========================
# Редактирование записи «группы риска»
# ==========================

@risk_groups_bp.route('/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_risk(record_id):
    """
    Редактирование существующей записи «группы риска».
    Можно менять уровень риска, причину, статус, дату снятия.
    """
    record = RiskGroup.query.get_or_404(record_id)
    form = RiskGroupForm(obj=record)
    _populate_risk_form_choices(form)

    if form.validate_on_submit():
        record.student_id = form.student_id.data
        record.date_added = form.date_added.data
        record.risk_level = form.risk_level.data
        record.reason = form.reason.data.strip() if form.reason.data else None
        record.status = form.status.data
        record.date_removed = form.date_removed.data if form.date_removed.data else None

        db.session.commit()
        flash('Запись «группы риска» успешно обновлена.', 'success')
        return redirect(url_for('risk_groups.list_risk'))

    return render_template(
        'risk_groups/form.html',
        form=form,
        title='Редактирование записи «группы риска»',
    )


# ==========================
# Быстрое снятие с учёта
# ==========================

@risk_groups_bp.route('/<int:record_id>/close', methods=['POST'])
@login_required
def close_risk(record_id):
    """
    Быстрое снятие студента с учёта «группы риска»:
      - статус -> 'снят'
      - дата снятия -> сегодняшняя, если не задана
    """
    record = RiskGroup.query.get_or_404(record_id)
    record.status = 'снят'
    if not record.date_removed:
        record.date_removed = date.today()

    db.session.commit()
    flash('Студент снят с учёта «группы риска».', 'success')
    return redirect(url_for('risk_groups.list_risk'))


# ==========================
# Удаление записи (по желанию)
# ==========================

@risk_groups_bp.route('/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_risk(record_id):
    """
    Полное удаление записи «группы риска».
    Обычно достаточно менять статус на «снят», но возможность удалить тоже оставляем.
    """
    record = RiskGroup.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    flash('Запись «группы риска» удалена.', 'success')
    return redirect(url_for('risk_groups.list_risk'))
