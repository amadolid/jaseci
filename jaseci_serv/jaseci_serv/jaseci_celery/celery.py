import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jaseci_serv.jaseci_serv.settings")

app = Celery("jaseci_celery", broker="amqp://guest@localhost//")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
