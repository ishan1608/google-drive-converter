from ffmpy import FFmpeg


class VideoConverter(object):
    @classmethod
    def convert(cls):
        ff = FFmpeg(
            inputs={'input.avi': None},
            outputs={'output.mp4': '-c:a aac -b:a 128k -c:v libx264 -crf 23 -vf scale=320:240'}
        )
        ff.run()
        print('conversion finished')

