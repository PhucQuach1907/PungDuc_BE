from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PungDuc_BE.settings')

app = Celery('PungDuc_BE')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.enable_utc = False

app.conf.update(timezone='Asia/Ho_Chi_Minh')

app.autodiscover_tasks()
