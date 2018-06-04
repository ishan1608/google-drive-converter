import os

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import CharField, NullBooleanField, EmailField
from model_utils import Choices
from model_utils.models import TimeStampedModel

from .utils import DriveDownloader, VideoConverter, S3Uploader


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
    recipient_email = EmailField()

    @classmethod
    def initialize_job(cls, shareable_link, quality, recipient):
        from celery_tasks import conversion_task

        drive_job = DriveJob.objects.create(
            drive_shareable_link=shareable_link,
            quality=quality,
            recipient_email=recipient
        )
        if settings.CELERY_ENABLED:
            conversion_task.delay(drive_job.id)
        else:
            drive_job.execute()
        return drive_job

    def execute(self):
        print('Execute Job: {}, with quality: {} and link: {}'.format(self.id, self.quality, self.drive_shareable_link))
        self.download_status = False
        self.save()
        # Download File
        downloaded_file_path = 'downloaded/{}'.format(self.id)
        DriveDownloader().download_shareable_link(self.drive_shareable_link, downloaded_file_path)

        self.download_status = True
        self.conversion_status = False
        self.save()

        # Convert File
        output_file_path = 'downloaded/output-{}.mp4'.format(self.id)
        log_path = 'downloaded/log-{}.log'.format(self.id)
        VideoConverter.convert(downloaded_file_path, output_file_path, log_path, self.quality)

        self.conversion_status = True
        self.upload_status = False
        self.save()

        # Delete downloaded file
        os.remove(downloaded_file_path)

        # Upload File
        converted_path = 'converted-{}.mp4'.format(self.id)
        S3Uploader.upload(output_file_path, converted_path)

        self.upload_status = True
        self.result_link = 'https://s3.amazonaws.com/google-drive-converter/{}'.format(converted_path)
        self.save()

        # Delete Converted File
        os.remove(output_file_path)

        # Send email

        send_mail(
            'Your download is ready',
'''The file you requested is ready to be downloaded:
Submitted Link: {}
Chosen Quality: {}
Download LInk: {}
--
http://www.ishan1608.space
'''.format(self.drive_shareable_link, self.quality, self.result_link),
            'notifications-no-reply@ishan1608.space',
            [self.recipient_email]
        )

    def __str__(self):
        return 'Job: {}:{}'.format(self.id, self.drive_shareable_link)
