from urllib.parse import urlparse

import requests
import boto3
from ffmpy import FFmpeg


class VideoConverter(object):
    @classmethod
    def convert(cls):
        ff = FFmpeg(
            inputs={'input.avi': None},
            outputs={'output.mp4': '-c:a aac -b:a 128k -c:v libx264 -crf 23 -vf scale=320:240'}
        )
        print(ff.cmd)
        with open('conversion-log.txt', 'w+') as log_file:
            ff.run(stdout=log_file, stderr=log_file)
            print('conversion finished')


class DriveDownloader(object):
    # taken from this StackOverflow answer: https://stackoverflow.com/a/39225039

    def download_shareable_link(self, shareable_link, output_file_name):
        drive_file_id = urlparse(shareable_link).query.split('=')[-1]
        self._download_file_from_google_drive(drive_file_id, output_file_name)

    def _download_file_from_google_drive(self, id, destination):
        url = "https://docs.google.com/uc?export=download"

        session = requests.Session()

        response = session.get(url, params={'id': id}, stream=True)
        token = self.get_confirm_token(response)

        if token:
            params = {'id': id, 'confirm': token}
            response = session.get(url, params=params, stream=True)

        self.save_response_content(response, destination)

    def get_confirm_token(self, response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(self, response, destination):
        CHUNK_SIZE = 32768

        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)


class S3Uploader(object):

    @classmethod
    def upload(cls, file_path):
        s3 = boto3.resource('s3')
        uploaded_file = s3.Bucket('google-drive-converter').upload_file(file_path, 'performance-pattern.mp4', Callback=print)
        print('Upload to S3 finished')
