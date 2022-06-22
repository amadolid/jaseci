from .celery import app
from .worker import per_minute, daily

from celery.schedules import crontab


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(), per_minute.s(), name="cron_daily")

    sender.add_periodic_task(
        crontab(minute=0, hour=0), daily.s(), name="cron_per_minute"
    )
