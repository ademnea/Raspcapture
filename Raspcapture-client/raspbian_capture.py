import config
import time
from picamera import PiCamera
import uuid
import pyaudio
import wave


class Capture:
    def __init__(self):
        self.files = []
        self.camera = None

    def record_video(self, capture_duration=10):
        self.init_camera()
        vid_path = config.video_dir + 'vid' + uuid.uuid4().__str__() + '.h264'
        self.camera.start_recording(vid_path)
        self.camera.wait_recording(capture_duration)
        self.camera.stop_recording()
        self.files.append([vid_path, "video"])
        self.save_to_db()

    def record_audio(self, record_seconds=10):
        chunk = 1024
        form = pyaudio.paInt16
        channels = 2
        rate = 44100

        p = pyaudio.PyAudio()

        stream = p.open(format=form,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

        frames = []

        for i in range(0, int(rate / chunk * record_seconds)):
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()
        aud_path = config.audio_dir + 'aud' + uuid.uuid4().__str__() + '.wav'
        wf = wave.open(aud_path, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(form))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        self.files.append([aud_path, "audio"])
        self.save_to_db()

    def init_camera(self):
        if self.camera is None:
            self.camera = PiCamera()
            self.camera.resolution = (640, 480)

    def snap(self, num=1):
        self.init_camera()
        time.sleep(2)
        for i in range(num):
            img_path = config.image_dir + 'img' + uuid.uuid4().__str__() + '.jpg'
            self.camera.capture(img_path)
            self.files.append([img_path, "image"])
        self.save_to_db()

    def save_to_db(self):
        pass
