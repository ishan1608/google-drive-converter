from django.db.models import CharField, NullBooleanField
from model_utils import Choices
from model_utils.models import TimeStampedModel


class DriveJob(TimeStampedModel):
    QUALITY_CHOICES = Choices(
        ('144p', '144p'),
        ('240p', '240p'),
        ('360p', '360p'),
        ('480p', '480p'),
        ('720p', '720p'),
        ('1080p', '1080p'),
    )

    scheduled_job_id = CharField(max_length=36, null=True)
    drive_shareable_link = CharField(max_length=2048)
    download_status = NullBooleanField()
    conversion_status = NullBooleanField()
    upload_status = NullBooleanField()
    result_link = CharField(max_length=2048, null=True)
    quality = CharField(max_length=8, choices=QUALITY_CHOICES, default='360p')

    @classmethod
    def initialize_job(cls, shareable_link, quality):
        drive_job = DriveJob.objects.create(
            drive_shareable_link=shareable_link,
            quality=quality
        )
        drive_job.execute()

    def execute(self):
        print(u'Execute Job: {}, with quality: {} and link: {}'.format(self.id, self.quality, self.drive_shareable_link))
