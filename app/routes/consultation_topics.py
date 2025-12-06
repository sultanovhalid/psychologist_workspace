from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required

from app.models import db, ConsultationTopic, Consultation
from app.forms import ConsultationTopicForm

consultation_topics_bp = Blueprint(
    'consultation_topics',
    __name__,
    url_prefix='/consultation_topics'
)


# ==========================
# Список тематик консультаций
# ==========================
@consultation_topics_bp.route('/', methods=['GET'])
@login_required
def list_topics():
    """
    Справочник тематик консультаций.
    Показываем все тематики, сначала активные, потом неактивные.
    """
    topics = (
        ConsultationTopic.query
        .order_by(ConsultationTopic.is_active.desc(), ConsultationTopic.name.asc())
        .all()
    )
    return render_template('consultation_topics/list.html', topics=topics)


# ==========================
# Создание тематики
# ==========================
@consultation_topics_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_topic():
    form = ConsultationTopicForm()
    if form.validate_on_submit():
        topic = ConsultationTopic(
            name=form.name.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            is_active=form.is_active.data,
        )
        db.session.add(topic)
        db.session.commit()
        flash('Тематика консультации успешно добавлена.', 'success')
        return redirect(url_for('consultation_topics.list_topics'))

    return render_template(
        'consultation_topics/form.html',
        form=form,
        title='Новая тематика консультации'
    )


# ==========================
# Редактирование тематики
# ==========================
@consultation_topics_bp.route('/<int:topic_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_topic(topic_id):
    topic = ConsultationTopic.query.get_or_404(topic_id)
    form = ConsultationTopicForm(obj=topic)

    if form.validate_on_submit():
        topic.name = form.name.data.strip()
        topic.description = form.description.data.strip() if form.description.data else None
        topic.is_active = form.is_active.data

        db.session.commit()
        flash('Тематика консультации успешно обновлена.', 'success')
        return redirect(url_for('consultation_topics.list_topics'))

    return render_template(
        'consultation_topics/form.html',
        form=form,
        title='Редактирование тематики консультации'
    )


# ==========================
# Удаление тематики
# ==========================
@consultation_topics_bp.route('/<int:topic_id>/delete', methods=['POST'])
@login_required
def delete_topic(topic_id):
    topic = ConsultationTopic.query.get_or_404(topic_id)

    # Проверяем, не используется ли тематика в консультациях
    consultations_count = Consultation.query.filter_by(topic_id=topic.id).count()
    if consultations_count > 0:
        flash(
            'Невозможно удалить тематику: есть консультации, '
            'в которых она используется. '
            'Вы можете снять галочку "Активна" вместо удаления.',
            'danger'
        )
        return redirect(url_for('consultation_topics.list_topics'))

    db.session.delete(topic)
    db.session.commit()
    flash('Тематика консультации успешно удалена.', 'success')
    return redirect(url_for('consultation_topics.list_topics'))
