from abc import ABCMeta
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment
import tempfile

from config import REQUIRED_COUNT_CHANNELS, REQUIRED_FRAME_RATE
from logger import ColorLogger
log = ColorLogger(name="Media").get_logger()


class ConvertedAudio:

    def __init__(self, path):
        self.path = path


class Media(metaclass=ABCMeta):

    def convert_audio_to_required_format(self, path: str) -> ConvertedAudio:
        log.info("Converting audio to standard format: %s", path)
        suffix = path[path.rindex('.') + 1:].lower()
        log.debug("Current suffix: %s", suffix)
        audio_segment = AudioSegment.from_file(path, format='ogg')
        audio_segment = self._setup_default_params(audio_segment=audio_segment)
        converted_audio_path = self._save_segment(audio_segment=audio_segment)
        converted_audio = ConvertedAudio(converted_audio_path)
        return converted_audio

    def _setup_default_params(self, audio_segment: AudioSegment) -> AudioSegment:
        audio_segment = audio_segment.set_channels(
            channels=REQUIRED_COUNT_CHANNELS)
        audio_segment = audio_segment.set_frame_rate(
            frame_rate=REQUIRED_FRAME_RATE)

        return audio_segment

    def _save_segment(self, audio_segment: AudioSegment) -> str:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            converted_audio_path = temp_file.name
            audio_segment.export(converted_audio_path, format="wav")
        return converted_audio_path


class Audio(Media):

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.format = self.file_path[self.file_path.rindex('.'):].lower()
        self.audio_segment = AudioSegment.from_file(file_path, format=self.format)


class Video(Media):

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.audiotrack_path = self._save_audiotrack()
        self.format = self.file_path[self.file_path.rindex('.'):].lower()

    def _save_audiotrack(self) -> str:
        video_file_clip = VideoFileClip(self.file_path)
        audio_file_clip = video_file_clip.audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            audiotrack_path = temp_file.name
            audio_file_clip.write_audiofile(audiotrack_path, codec="pcm_s16le")

        return audiotrack_path

    def merge(self, audiotrack_path: str) -> str:
        log.debug("audiotrack_path: %s", audiotrack_path)
        audio_file_clip = AudioFileClip(audiotrack_path)
        video_file_clip = VideoFileClip(self.file_path).set_audio(audio_file_clip)
        complited_video_path = self._save_video(video_file_clip)
        return complited_video_path

    def _save_video(self, video_file_clip: VideoFileClip) -> str:
        format = self.format
        with tempfile.NamedTemporaryFile(suffix=format, delete=False) as temp_file:
            log.debug('video_path: %s', temp_file)
            completed_video_path = temp_file.name
            log.debug('completed_video_path: %s', completed_video_path)
            video_file_clip.write_videofile(completed_video_path, codec="libx264")
        return completed_video_path
