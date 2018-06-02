from model_utils.models import TimeStampedModel
from django.db.models import CharField, NullBooleanField


class DriveJob(TimeStampedModel):
    scheduled_job_id = CharField(max_length=36, null=True)
    drive_shareable_link = CharField(max_length=2048)
    download_status = NullBooleanField()
    conversion_status = NullBooleanField()
    upload_status = NullBooleanField()
    result_link = CharField(max_length=2048, null=True)
