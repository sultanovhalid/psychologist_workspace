from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.models import (
    db,
    Student,
    User,
    PsychologicalTest,
    TestResult,
)
from app.forms import (
    PsychologicalTestForm,
    TestResultForm,
)

diagnostics_bp = Blueprint(
    'diagnostics',
    __name__,
    url_prefix='/diagnostics'
)


# ==========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================

def _populate_test_result_form_choices(form: TestResultForm):
    """Заполняем списки студентов, методик и психологов для формы результатов тестирования."""
    # Студенты
    students = Student.query.order_by(Student.full_name.asc()).all()
    form.student_id.choices = [(s.id, s.full_name) for s in students]

    # Методики
    tests = PsychologicalTest.query.order_by(PsychologicalTest.name.asc()).all()
    form.test_id.choices = [(t.id, t.name) for t in tests]

    # Психологи (psychologist + admin)
    psychologists = (
        User.query
        .filter(User.role.in_(['psychologist', 'admin']))
        .order_by(User.full_name.asc())
        .all()
    )
    form.psychologist_id.choices = [(0, '— Не указан —')] + [
        (u.id, u.full_name or u.username) for u in psychologists
    ]


# ==========================
# СПРАВОЧНИК МЕТОДИК (PsychologicalTest)
# ==========================

@diagnostics_bp.route('/tests', methods=['GET'])
@login_required
def list_tests():
    """Список психодиагностических методик."""
    tests = PsychologicalTest.query.order_by(PsychologicalTest.name.asc()).all()
    return render_template(
        'diagnostics/tests_list.html',
        tests=tests,
    )


@diagnostics_bp.route('/tests/create', methods=['GET', 'POST'])
@login_required
def create_test():
    """Создание новой методики."""
    form = PsychologicalTestForm()
    if form.validate_on_submit():
        test = PsychologicalTest(
            name=form.name.data.strip(),
            short_name=form.short_name.data.strip() if form.short_name.data else None,
            description=form.description.data.strip() if form.description.data else None,
            target_group=form.target_group.data.strip() if form.target_group.data else None,
        )
        db.session.add(test)
        db.session.commit()
        flash('Методика успешно добавлена.', 'success')
        return redirect(url_for('diagnostics.list_tests'))

    return render_template(
        'diagnostics/test_form.html',
        form=form,
        title='Новая психодиагностическая методика',
    )


@diagnostics_bp.route('/tests/<int:test_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_test(test_id):
    """Редактирование методики."""
    test = PsychologicalTest.query.get_or_404(test_id)
    form = PsychologicalTestForm(obj=test)

    if form.validate_on_submit():
        test.name = form.name.data.strip()
        test.short_name = form.short_name.data.strip() if form.short_name.data else None
        test.description = form.description.data.strip() if form.description.data else None
        test.target_group = form.target_group.data.strip() if form.target_group.data else None

        db.session.commit()
        flash('Методика успешно обновлена.', 'success')
        return redirect(url_for('diagnostics.list_tests'))

    return render_template(
        'diagnostics/test_form.html',
        form=form,
        title='Редактирование методики',
    )


@diagnostics_bp.route('/tests/<int:test_id>/delete', methods=['POST'])
@login_required
def delete_test(test_id):
    """Удаление методики (если нет результатов, где она используется)."""
    test = PsychologicalTest.query.get_or_404(test_id)

    results_count = TestResult.query.filter_by(test_id=test.id).count()
    if results_count > 0:
        flash(
            'Невозможно удалить методику: существуют результаты тестирования, '
            'в которых она используется.',
            'danger'
        )
        return redirect(url_for('diagnostics.list_tests'))

    db.session.delete(test)
    db.session.commit()
    flash('Методика успешно удалена.', 'success')
    return redirect(url_for('diagnostics.list_tests'))


# ==========================
# РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ (TestResult)
# ==========================

@diagnostics_bp.route('/results', methods=['GET'])
@login_required
def list_results():
    """
    Список результатов тестирования.
    Фильтры: по студенту и по методике (через query-параметры).
    """
    student_id = request.args.get('student_id', type=int)
    test_id = request.args.get('test_id', type=int)

    query = TestResult.query

    if student_id:
        query = query.filter(TestResult.student_id == student_id)
    if test_id:
        query = query.filter(TestResult.test_id == test_id)

    results = query.order_by(TestResult.date.desc()).all()

    students = Student.query.order_by(Student.full_name.asc()).all()
    tests = PsychologicalTest.query.order_by(PsychologicalTest.name.asc()).all()

    return render_template(
        'diagnostics/results_list.html',
        results=results,
        students=students,
        tests=tests,
        selected_student_id=student_id,
        selected_test_id=test_id,
    )


@diagnostics_bp.route('/results/create', methods=['GET', 'POST'])
@login_required
def create_result():
    """Создание нового результата тестирования."""
    form = TestResultForm()
    _populate_test_result_form_choices(form)

    # По умолчанию подставляем текущего пользователя как психолога
    if request.method == 'GET' and current_user.is_authenticated:
        for value, label in form.psychologist_id.choices:
            if value == current_user.id:
                form.psychologist_id.data = current_user.id
                break

    if form.validate_on_submit():
        psychologist_id = form.psychologist_id.data if form.psychologist_id.data != 0 else None

        result = TestResult(
            date=form.date.data,
            student_id=form.student_id.data,
            test_id=form.test_id.data,
            raw_score=form.raw_score.data.strip() if form.raw_score.data else None,
            level=form.level.data.strip() if form.level.data else None,
            comment=form.comment.data.strip() if form.comment.data else None,
            psychologist_id=psychologist_id,
        )
        db.session.add(result)
        db.session.commit()
        flash('Результат тестирования успешно добавлен.', 'success')
        return redirect(url_for('diagnostics.list_results'))

    return render_template(
        'diagnostics/result_form.html',
        form=form,
        title='Новый результат тестирования',
    )


@diagnostics_bp.route('/results/<int:result_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_result(result_id):
    """Редактирование результата тестирования."""
    result = TestResult.query.get_or_404(result_id)
    form = TestResultForm(obj=result)
    _populate_test_result_form_choices(form)

    if request.method == 'GET':
        # Преобразуем None -> 0 для SelectField психолога
        form.psychologist_id.data = result.psychologist_id or 0

    if form.validate_on_submit():
        result.date = form.date.data
        result.student_id = form.student_id.data
        result.test_id = form.test_id.data
        result.raw_score = form.raw_score.data.strip() if form.raw_score.data else None
        result.level = form.level.data.strip() if form.level.data else None
        result.comment = form.comment.data.strip() if form.comment.data else None
        result.psychologist_id = form.psychologist_id.data if form.psychologist_id.data != 0 else None

        db.session.commit()
        flash('Результат тестирования успешно обновлён.', 'success')
        return redirect(url_for('diagnostics.list_results'))

    return render_template(
        'diagnostics/result_form.html',
        form=form,
        title='Редактирование результата тестирования',
    )


@diagnostics_bp.route('/results/<int:result_id>/delete', methods=['POST'])
@login_required
def delete_result(result_id):
    """Удаление результата тестирования."""
    result = TestResult.query.get_or_404(result_id)
    db.session.delete(result)
    db.session.commit()
    flash('Результат тестирования успешно удалён.', 'success')
    return redirect(url_for('diagnostics.list_results'))
