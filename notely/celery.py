import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notely.settings')

app = Celery('notely')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost')
app.conf.update(BROKER_URL=REDIS_URL, CELERY_RESULT_BACKEND=REDIS_URL)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
