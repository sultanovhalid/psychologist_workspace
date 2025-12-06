from datetime import datetime

from flask import Blueprint, render_template, request
from flask_login import login_required

from app.models import (
    Consultation,
    Group,
    Student,
    GroupEvent,
    RiskGroup,
    TestResult,
    PsychologicalTest,
)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('/')
@login_required
def overview():
    # -------- Фильтры --------
    group_id = request.args.get('group_id', type=int)
    consultation_type = request.args.get('type', type=str)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    dt_start = None
    dt_end = None
    if start_date_str:
        dt_start = datetime.strptime(start_date_str, '%Y-%m-%d')
    if end_date_str:
        # чтобы включить весь день, можно сдвинуться до конца суток
        dt_end = datetime.strptime(end_date_str, '%Y-%m-%d')

    # -------- Консультации --------
    consultations_query = Consultation.query

    if group_id:
        consultations_query = consultations_query.filter_by(group_id=group_id)
    if consultation_type:
        consultations_query = consultations_query.filter_by(consultation_type=consultation_type)
    if dt_start:
        consultations_query = consultations_query.filter(Consultation.date >= dt_start)
    if dt_end:
        consultations_query = consultations_query.filter(Consultation.date <= dt_end)

    consultations = consultations_query.all()
    groups = Group.query.order_by(Group.name.asc()).all()

    total = len(consultations)

    by_type = {}
    for c in consultations:
        by_type[c.consultation_type] = by_type.get(c.consultation_type, 0) + 1

    by_group = {}
    for c in consultations:
        g = Group.query.get(c.group_id)
        if g:
            by_group[g.name] = by_group.get(g.name, 0) + 1

    chart_data = {
        "labels": list(by_type.keys()),
        "values": list(by_type.values())
    }
    group_chart_data = {
        "labels": list(by_group.keys()),
        "values": list(by_group.values())
    }

    # -------- Групповые мероприятия --------
    events_query = GroupEvent.query
    if group_id:
        events_query = events_query.filter(GroupEvent.group_id == group_id)
    if dt_start:
        events_query = events_query.filter(GroupEvent.date >= dt_start)
    if dt_end:
        events_query = events_query.filter(GroupEvent.date <= dt_end)

    events = events_query.all()
    events_total = len(events)

    events_by_type = {}
    for e in events:
        events_by_type[e.event_type] = events_by_type.get(e.event_type, 0) + 1

    events_chart_data = {
        "labels": list(events_by_type.keys()),
        "values": list(events_by_type.values())
    }

    # -------- Группа риска --------
    # фильтрация по группе и датам постановки
    risk_query = RiskGroup.query.join(Student, RiskGroup.student_id == Student.id)
    if group_id:
        risk_query = risk_query.filter(Student.group_id == group_id)
    if dt_start:
        risk_query = risk_query.filter(RiskGroup.date_added >= dt_start.date())
    if dt_end:
        risk_query = risk_query.filter(RiskGroup.date_added <= dt_end.date())

    risk_records = risk_query.all()
    risk_total = len(risk_records)
    risk_active = sum(1 for r in risk_records if r.status == 'активен')

    risk_by_level = {}
    for r in risk_records:
        risk_by_level[r.risk_level] = risk_by_level.get(r.risk_level, 0) + 1

    risk_chart_data = {
        "labels": list(risk_by_level.keys()),
        "values": list(risk_by_level.values())
    }

    # -------- Диагностика (результаты тестирования) --------
    results_query = TestResult.query.join(Student, TestResult.student_id == Student.id)
    if group_id:
        results_query = results_query.filter(Student.group_id == group_id)
    if dt_start:
        results_query = results_query.filter(TestResult.date >= dt_start)
    if dt_end:
        results_query = results_query.filter(TestResult.date <= dt_end)

    test_results = results_query.all()
    test_results_total = len(test_results)
    tests_total = PsychologicalTest.query.count()

    # распределение по методикам
    results_by_test = {}
    for r in test_results:
        test_name = r.test.short_name or r.test.name if r.test else 'Не указана'
        results_by_test[test_name] = results_by_test.get(test_name, 0) + 1

    results_by_level = {}
    for r in test_results:
        lvl = r.level or 'Не указан'
        results_by_level[lvl] = results_by_level.get(lvl, 0) + 1

    test_by_test_chart = {
        "labels": list(results_by_test.keys()),
        "values": list(results_by_test.values())
    }
    test_by_level_chart = {
        "labels": list(results_by_level.keys()),
        "values": list(results_by_level.values())
    }

    return render_template(
        'analytics/overview.html',
        # фильтры
        groups=groups,
        group_id=group_id,
        consultation_type=consultation_type,
        start_date=start_date_str,
        end_date=end_date_str,

        # консультации
        total=total,
        consultations=consultations,
        chart_data=chart_data,
        group_chart_data=group_chart_data,

        # групповые мероприятия
        events=events,
        events_total=events_total,
        events_chart_data=events_chart_data,

        # группа риска
        risk_records=risk_records,
        risk_total=risk_total,
        risk_active=risk_active,
        risk_chart_data=risk_chart_data,

        # диагностика
        test_results=test_results,
        test_results_total=test_results_total,
        tests_total=tests_total,
        test_by_test_chart=test_by_test_chart,
        test_by_level_chart=test_by_level_chart,
    )
