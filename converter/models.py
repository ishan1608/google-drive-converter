import os
from urllib.parse import quote

from django.conf import settings
from django.core.mail import EmailMessage
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
    file_name_suffix = CharField(max_length=1024)

    @classmethod
    def initialize_job(cls, shareable_link, quality, recipient, file_name_suffix):
        from celery_tasks import conversion_task

        drive_job = DriveJob.objects.create(
            drive_shareable_link=shareable_link,
            quality=quality,
            recipient_email=recipient,
            file_name_suffix=file_name_suffix
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
        downloaded_file_path = 'downloaded/{}-{}'.format(self.id, self.file_name_suffix)
        DriveDownloader().download_shareable_link(self.drive_shareable_link, downloaded_file_path)

        self.download_status = True
        self.conversion_status = False
        self.save()

        output_file_path = 'downloaded/output-{}-{}.mp4'.format(self.id, self.file_name_suffix)
        self.convert_video(downloaded_file_path, output_file_path)

        # Upload File
        self.upload_video(output_file_path)

        # Send email
        self.send_email()

    def convert_video(self, downloaded_file_path, output_file_path):
        # Convert File
        log_path = 'downloaded/log-{}-{}.log'.format(self.id, self.file_name_suffix)
        VideoConverter.convert(downloaded_file_path, output_file_path, log_path, self.quality)

        self.conversion_status = True
        self.upload_status = False
        self.save()

        # Delete downloaded file
        os.remove(downloaded_file_path)

    def upload_video(self, output_file_path):
        converted_path = 'converted-{}-{}.mp4'.format(self.id, self.file_name_suffix)
        S3Uploader.upload(output_file_path, converted_path)

        self.upload_status = True
        self.result_link = 'https://s3.amazonaws.com/google-drive-converter/{}'.format(quote(converted_path))
        self.save()

        # Delete Converted File
        os.remove(output_file_path)

    def send_email(self):
        email = EmailMessage('Your download is ready',
                             '''The file you requested is ready to be downloaded:
                                         Submitted Link: {}
                                         Chosen Quality: {}
                                         Download LInk: {}
                                         File Name Suffix: {}
                                         --
                                         http://www.ishan1608.space
                                         '''.format(self.drive_shareable_link, self.quality,
                                                    self.result_link,
                                                    self.file_name_suffix),
                             'notifications-no-reply@ishan1608.space',
                             to=[self.recipient_email],
                             bcc=settings.ADMINS
                             )
        email.send()

    def __str__(self):
        return 'Job: {}:{}'.format(self.id, self.drive_shareable_link)
