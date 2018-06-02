from urllib.parse import urlparse

import requests
import boto3
from ffmpy import FFmpeg
import os


class VideoConverter(object):
    @classmethod
    def convert(cls, input_path, destination_path, log_path, quality):
        resolution_map = {
            '144p': {
                'width': 256,
                'height': 144
            },
            '240p': {
                'width': 426,
                'height': 240
            },
            '360p': {
                'width': 640,
                'height': 360
            },
            '480p': {
                'width': 854,
                'height': 480
            },
            '720p': {
                'width': 1280,
                'height': 720
            },
            '1080p': {
                'width': 1920,
                'height': 1080
            },
        }
        # Cleanup the destination path
        if os.path.exists(destination_path):
            os.remove(destination_path)

        dimensions = resolution_map[quality]
        ff = FFmpeg(
            inputs={input_path: None},
            outputs={destination_path: '-c:a aac -b:a 128k -c:v libx264 -crf 23 -vf scale={width}:{height}'.format(
                width=dimensions['width'], height=dimensions['height'])
            }
        )
        print(ff.cmd)
        with open(log_path, 'w+') as log_file:
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
    def upload(cls, file_path, file_key):
        s3 = boto3.resource('s3')
        s3.Bucket('google-drive-converter').upload_file(file_path, file_key, Callback=print)
        print('Upload to S3 finished')
