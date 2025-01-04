from abc import ABCMeta
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment
import tempfile

from config import REQUIRED_COUNT_CHANNELS, REQUIRED_FRAME_RATE


class ConvertedAudio:

    def __init__(self, path):
        self.path = path


class Media(metaclass=ABCMeta):

    def convert_audio_to_required_format(self, path: str) -> ConvertedAudio:
        audio_segment = AudioSegment.from_file(path)
        audio_segment = self._setup_default_params(audio_segment=audio_segment)
        converted_audio_path = self._save_segment(audio_segment=audio_segment)
        converted_audio = ConvertedAudio(converted_audio_path)
        return converted_audio

    def _setup_default_params(self, audio_segment: AudioSegment) -> AudioSegment:
        audio_segment = audio_segment.set_channels(
            channels=REQUIRED_COUNT_CHANNELS)
        audio_segment = audio_segment.set_frame_rate(
            frame_rate=REQUIRED_FRAME_RATE)

    def _save_segment(self, audio_segment: AudioSegment) -> str:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            converted_audio_path = temp_file.name
            audio_segment.export(converted_audio_path, format="wav")
        return converted_audio_path


class Audio(Media):

    def __init__(self, file_path: str):
        self.file_path = file_path


class Video(Media):

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.audiotrack_path = self._save_audiotrack()

    def _save_audiotrack(self) -> str:
        video_file_clip = VideoFileClip(self.file_path)
        audio_file_clip = video_file_clip.audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            audiotrack_path = temp_file.name
            audio_file_clip.write_audiofile(audiotrack_path, codec="pcm_s16le")

        return audiotrack_path

    def merge(self, audiotrack_path: str) -> str:
        audio_file_clip = AudioFileClip(audiotrack_path)
        video_file_clip = VideoFileClip(
            self.file_path).set_audio(audio_file_clip)
        complited_video_path = self._save_video(video_file_clip)
        return complited_video_path

    def _save_video(self, video_file_clip: VideoFileClip) -> str:
        suffix = self.file_path[self.file_path.rindex('.') + 1:]
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            complited_video_path = temp_file.name
            video_file_clip.write_videofile(complited_video_path, format=suffix)
        return complited_video_path