import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.environ.get('SECRET_KEY') or 'very_secret_key_for_demo'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'app.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-WTF
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = SECRET_KEY

# Создать instance/ если нет
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
os.makedirs(INSTANCE_DIR, exist_ok=True)

# Папка для экспорта (экспорт CSV/Excel)
EXPORT_DIR = os.path.join(BASE_DIR, 'app', 'export')
os.makedirs(EXPORT_DIR, exist_ok=True)
