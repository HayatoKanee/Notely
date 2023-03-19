import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notely.settings')

app = Celery('notely')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.broker_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
