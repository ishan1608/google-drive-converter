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

