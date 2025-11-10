import csv
import pandas as pd
from app.models import Consultation, Student, Group

def export_consultations_to_csv(consultations, filepath):
    """Экспорт списка консультаций в CSV (разделитель ;, совместимо с 1С)."""
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

def export_consultations_to_excel(consultations, filepath):
    """Экспорт списка консультаций в Excel (.xlsx)."""
    rows = []
    for c in consultations:
        student = Student.query.get(c.student_id)
        group = Group.query.get(c.group_id) if c.group_id else None
        rows.append({
            'Дата': c.date.strftime('%Y-%m-%d %H:%M'),
            'ФИО студента': student.full_name if student else '',
            'Группа': group.name if group else '',
            'Тема': c.topic,
            'Тип консультации': c.consultation_type,
            'Результат': c.result or '',
            'Психолог': c.psychologist or ''
        })
    df = pd.DataFrame(rows)
    df.to_excel(filepath, index=False)

def import_students_from_csv(filepath):
    """Импорт студентов из CSV с полями: ФИО;Группа;Дата рождения"""
    imported = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            full_name = row.get('ФИО') or row.get('ФИО студента') or ''
            group_name = row.get('Группа') or ''
            date_of_birth = row.get('Дата рождения') or None
            group = Group.query.filter_by(name=group_name).first() if group_name else None
            imported.append({
                'full_name': full_name.strip(),
                'group_id': group.id if group else None,
                'date_of_birth': date_of_birth
            })
    return imported
