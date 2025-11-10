import os
import uuid
from werkzeug.utils import secure_filename

def make_safe_filename(filename):
    """
    Преобразует имя файла к безопасному для хранения на диске.
    """
    name, ext = os.path.splitext(filename)
    safe = secure_filename(name)
    unique = uuid.uuid4().hex[:8]
    return f"{safe}_{unique}{ext}"

def save_uploaded_file(uploaded_file, upload_dir):
    """
    Сохраняет загруженный файл в указанную директорию.
    Возвращает путь к сохранённому файлу.
    """
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    filename = make_safe_filename(uploaded_file.filename)
    filepath = os.path.join(upload_dir, filename)
    uploaded_file.save(filepath)
    return filepath

def delete_file(filepath):
    """
    Удаляет файл, если он существует.
    """
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception:
        pass
    return False

def file_exists(filepath):
    """
    Проверяет, существует ли файл.
    """
    return filepath and os.path.exists(filepath)
