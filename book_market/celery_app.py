import os
import time 
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_market.settings')
app = Celery('service')
app.config_from_object('django.conf:settings')
app.conf.broker_transport = 'redis'
app.conf.broker_url = settings.CELERY_BROKER_URL
# app.conf.broker_connection_retry_on_startup = True
# app.conf.celery_result_backend = 'redis://w2214.area1.company.com:6379/0'
# app.control.purge()
app.autodiscover_tasks()


@app.task
def debug_task():
    time.sleep()
    print('Hello, thats debug task!')
