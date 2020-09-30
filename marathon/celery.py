import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marathon.settings')

app = Celery('marathon')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.task_default_queue = 'default'
