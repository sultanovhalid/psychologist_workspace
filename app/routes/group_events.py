from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.models import db, GroupEvent, Group, User
from app.forms import GroupEventForm

group_events_bp = Blueprint(
    'group_events',
    __name__,
    url_prefix='/group_events'
)


def _populate_group_event_form_choices(form: GroupEventForm):
    """Подготовка списков групп и психологов для формы."""
    # Группы: добавляем вариант "не указана"
    groups = Group.query.order_by(Group.name.asc()).all()
    form.group_id.choices = [(0, '— Не выбрана —')] + [(g.id, g.name) for g in groups]

    # Психологи: по роли psychologist, админов можно тоже добавить при желании
    psychologists = (
        User.query
        .filter(User.role.in_(['psychologist', 'admin']))
        .order_by(User.full_name.asc())
        .all()
    )
    form.psychologist_id.choices = [(0, '— Не выбран —')] + [
        (u.id, u.full_name or u.username) for u in psychologists
    ]


# ==========================
# Список групповых мероприятий
# ==========================
@group_events_bp.route('/', methods=['GET'])
@login_required
def list_events():
    """
    Список групповых мероприятий.
    По умолчанию показываются все, отсортированные по дате (новые сверху).
    Можно добавить простые фильтры по группе/типу через query-параметры.
    """
    group_id = request.args.get('group_id', type=int)
    event_type = request.args.get('event_type', type=str)

    query = GroupEvent.query

    if group_id:
        query = query.filter(GroupEvent.group_id == group_id)

    if event_type:
        query = query.filter(GroupEvent.event_type == event_type)

    events = query.order_by(GroupEvent.date.desc()).all()
    groups = Group.query.order_by(Group.name.asc()).all()

    # Для фильтра по типу можно вытянуть уникальные значения из БД
    event_types = (
        db.session.query(GroupEvent.event_type)
        .distinct()
        .order_by(GroupEvent.event_type.asc())
        .all()
    )
    event_types = [et[0] for et in event_types]

    return render_template(
        'group_events/list.html',
        events=events,
        groups=groups,
        event_types=event_types,
        selected_group_id=group_id,
        selected_event_type=event_type,
    )


# ==========================
# Создание мероприятия
# ==========================
@group_events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = GroupEventForm()
    _populate_group_event_form_choices(form)

    # По умолчанию подставляем текущего пользователя как психолога (если он не анонимный)
    if request.method == 'GET' and current_user.is_authenticated:
        # проверяем, есть ли он в списке choices
        for value, label in form.psychologist_id.choices:
            if value == current_user.id:
                form.psychologist_id.data = current_user.id
                break

    if form.validate_on_submit():
        group_id = form.group_id.data if form.group_id.data != 0 else None
        psychologist_id = form.psychologist_id.data if form.psychologist_id.data != 0 else None

        event = GroupEvent(
            date=form.date.data,
            group_id=group_id,
            title=form.title.data.strip(),
            event_type=form.event_type.data,
            psychologist_id=psychologist_id,
            participants_count=form.participants_count.data,
            description=form.description.data.strip() if form.description.data else None,
        )
        db.session.add(event)
        db.session.commit()
        flash('Мероприятие успешно добавлено.', 'success')
        return redirect(url_for('group_events.list_events'))

    return render_template(
        'group_events/form.html',
        form=form,
        title='Новое групповое мероприятие'
    )


# ==========================
# Редактирование мероприятия
# ==========================
@group_events_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = GroupEvent.query.get_or_404(event_id)
    form = GroupEventForm(obj=event)
    _populate_group_event_form_choices(form)

    # Преобразуем None -> 0 для SelectField
    if request.method == 'GET':
        form.group_id.data = event.group_id or 0
        form.psychologist_id.data = event.psychologist_id or 0

    if form.validate_on_submit():
        event.date = form.date.data
        event.group_id = form.group_id.data if form.group_id.data != 0 else None
        event.title = form.title.data.strip()
        event.event_type = form.event_type.data
        event.psychologist_id = form.psychologist_id.data if form.psychologist_id.data != 0 else None
        event.participants_count = form.participants_count.data
        event.description = form.description.data.strip() if form.description.data else None

        db.session.commit()
        flash('Мероприятие успешно обновлено.', 'success')
        return redirect(url_for('group_events.list_events'))

    return render_template(
        'group_events/form.html',
        form=form,
        title='Редактирование мероприятия'
    )


# ==========================
# Удаление мероприятия
# ==========================
@group_events_bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = GroupEvent.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Мероприятие успешно удалено.', 'success')
    return redirect(url_for('group_events.list_events'))
