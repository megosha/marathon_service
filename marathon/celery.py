import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marathon.settings')

app = Celery('marathon')
app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks()
app.conf.task_default_queue = 'default'
