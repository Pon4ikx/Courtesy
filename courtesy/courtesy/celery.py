import os
from celery import Celery
from django.conf import settings

# Установите переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'courtesy.settings')

app = Celery('courtesy')

# Используйте строку настроек Django для настройки Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач в приложениях Django
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
