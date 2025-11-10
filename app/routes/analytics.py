from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models import Consultation, Group, Student
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
@login_required
def overview():
    # Фильтрация
    group_id = request.args.get('group_id', type=int)
    consultation_type = request.args.get('type', type=str)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    consultations_query = Consultation.query

    if group_id:
        consultations_query = consultations_query.filter_by(group_id=group_id)
    if consultation_type:
        consultations_query = consultations_query.filter_by(consultation_type=consultation_type)
    if start_date:
        consultations_query = consultations_query.filter(Consultation.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        consultations_query = consultations_query.filter(Consultation.date <= datetime.strptime(end_date, '%Y-%m-%d'))

    consultations = consultations_query.all()
    groups = Group.query.all()

    # Аналитика — подсчёты
    total = len(consultations)
    by_type = {}
    for c in consultations:
        by_type[c.consultation_type] = by_type.get(c.consultation_type, 0) + 1

    by_group = {}
    for c in consultations:
        g = Group.query.get(c.group_id)
        if g:
            by_group[g.name] = by_group.get(g.name, 0) + 1

    # Для диаграмм (передаются в шаблон)
    chart_data = {
        "labels": list(by_type.keys()),
        "values": list(by_type.values())
    }
    group_chart_data = {
        "labels": list(by_group.keys()),
        "values": list(by_group.values())
    }

    return render_template(
        'analytics/overview.html',
        total=total,
        consultations=consultations,
        groups=groups,
        group_id=group_id,
        consultation_type=consultation_type,
        start_date=start_date,
        end_date=end_date,
        chart_data=chart_data,
        group_chart_data=group_chart_data
    )
