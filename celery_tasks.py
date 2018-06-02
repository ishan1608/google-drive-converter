import os

import django
from celery import Celery

os.environ['DJANGO_SETTINGS_MODULE'] = "google_drive_converter.settings"
django.setup()


app = Celery('celery_tasks', broker='pyamqp://guest@localhost//')


@app.task
def conversion_task(job_id):
    from converter.models import DriveJob

    job = DriveJob.objects.get(id=job_id)
    print(u'Got Job: {}'.format(job))
    job.execute()
