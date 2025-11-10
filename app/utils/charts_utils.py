from collections import Counter
from app.models import Consultation, Group, Student
from datetime import datetime

def consultations_by_type(consultations):
    """Вернёт данные для круговой диаграммы по типам консультаций."""
    types = [c.consultation_type for c in consultations]
    counter = Counter(types)
    return {
        "labels": list(counter.keys()),
        "values": list(counter.values())
    }

def consultations_by_group(consultations):
    """Данные для диаграммы по группам."""
    group_names = []
    for c in consultations:
        if c.group_id:
            group = Group.query.get(c.group_id)
            group_names.append(group.name if group else "Без группы")
        else:
            group_names.append("Без группы")
    counter = Counter(group_names)
    return {
        "labels": list(counter.keys()),
        "values": list(counter.values())
    }

def consultations_by_month(consultations):
    """Динамика количества консультаций по месяцам (bar chart)."""
    months = [c.date.strftime('%Y-%m') for c in consultations]
    counter = Counter(months)
    # Сортировка по времени
    sorted_items = sorted(counter.items())
    return {
        "labels": [item[0] for item in sorted_items],
        "values": [item[1] for item in sorted_items]
    }
