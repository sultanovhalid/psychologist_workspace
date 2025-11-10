from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from app.models import db, Consultation, Student, Group
from app.forms import ConsultationForm, SearchForm
import csv
import os
from datetime import datetime

consultations_bp = Blueprint('consultations', __name__, url_prefix='/consultations')

# ----------- Список консультаций -----------
@consultations_bp.route('/', methods=['GET', 'POST'])
@login_required
def list_consultations():
    form = SearchForm()
    query = Consultation.query.order_by(Consultation.date.desc())

    # Фильтрация/поиск
    search = form.query.data if form.validate_on_submit() else request.args.get('query', '')
    if search:
        query = query.join(Student).filter(Student.full_name.ilike(f"%{search}%"))
    group_id = request.args.get('group_id', type=int)
    if group_id:
        query = query.filter(Consultation.group_id == group_id)

    consultations = query.all()
    groups = Group.query.all()
    return render_template('consultations/list.html', consultations=consultations, groups=groups, form=form, group_id=group_id, search=search)

# ----------- Добавить консультацию -----------
@consultations_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_consultation():
    form = ConsultationForm()
    students = Student.query.all()
    groups = Group.query.all()
    form.student_id.choices = [(s.id, s.full_name) for s in students]
    form.group_id.choices = [(0, '-')] + [(g.id, g.name) for g in groups]
    if form.validate_on_submit():
        consultation = Consultation(
            date=form.date.data,
            student_id=form.student_id.data,
            group_id=form.group_id.data if form.group_id.data else None,
            topic=form.topic.data,
            consultation_type=form.consultation_type.data,
            result=form.result.data,
            psychologist=form.psychologist.data or (current_user.full_name if hasattr(current_user, "full_name") else None)
        )
        db.session.add(consultation)
        db.session.commit()
        flash('Консультация добавлена.', 'success')
        return redirect(url_for('consultations.list_consultations'))
    return render_template('consultations/add_edit.html', form=form, edit=False)

# ----------- Редактировать консультацию -----------
@consultations_bp.route('/edit/<int:consultation_id>', methods=['GET', 'POST'])
@login_required
def edit_consultation(consultation_id):
    consultation = Consultation.query.get_or_404(consultation_id)
    form = ConsultationForm(obj=consultation)
    students = Student.query.all()
    groups = Group.query.all()
    form.student_id.choices = [(s.id, s.full_name) for s in students]
    form.group_id.choices = [(0, '-')] + [(g.id, g.name) for g in groups]
    if form.validate_on_submit():
        consultation.date = form.date.data
        consultation.student_id = form.student_id.data
        consultation.group_id = form.group_id.data if form.group_id.data else None
        consultation.topic = form.topic.data
        consultation.consultation_type = form.consultation_type.data
        consultation.result = form.result.data
        consultation.psychologist = form.psychologist.data or (current_user.full_name if hasattr(current_user, "full_name") else None)
        db.session.commit()
        flash('Данные консультации обновлены.', 'success')
        return redirect(url_for('consultations.list_consultations'))
    return render_template('consultations/add_edit.html', form=form, edit=True)

# ----------- Удалить консультацию -----------
@consultations_bp.route('/delete/<int:consultation_id>', methods=['POST'])
@login_required
def delete_consultation(consultation_id):
    consultation = Consultation.query.get_or_404(consultation_id)
    db.session.delete(consultation)
    db.session.commit()
    flash('Консультация удалена.', 'success')
    return redirect(url_for('consultations.list_consultations'))

# ----------- Экспорт в CSV для 1С -----------
@consultations_bp.route('/export')
@login_required
def export_consultations():
    # Выбираем все консультации
    consultations = Consultation.query.order_by(Consultation.date.desc()).all()

    # Файл CSV для 1С
    export_folder = os.path.join(current_app.root_path, 'export')
    os.makedirs(export_folder, exist_ok=True)
    filename = 'consultations_1c.csv'
    filepath = os.path.join(export_folder, filename)

    # Формируем CSV
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([
            'Дата', 'ФИО студента', 'Группа', 'Тема', 'Тип консультации', 'Результат', 'Психолог'
        ])
        for c in consultations:
            student = Student.query.get(c.student_id)
            group = Group.query.get(c.group_id) if c.group_id else None
            writer.writerow([
                c.date.strftime('%Y-%m-%d %H:%M'),
                student.full_name if student else '',
                group.name if group else '',
                c.topic,
                c.consultation_type,
                c.result or '',
                c.psychologist or ''
            ])

    flash('Экспортировано в consultations_1c.csv', 'success')
    return send_file(filepath, as_attachment=True)

