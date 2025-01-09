import os
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment
import tempfile

from logger import ColorLogger

log = ColorLogger(name="Media").get_logger()


class Audio:

    def __init__(self, file_path: str):
        base, ext = os.path.splitext(file_path)

        self.file_path: str = file_path
        self.extension: str = ext
        self.segment: AudioSegment = AudioSegment.from_file(self.file_path, format=self.extension[1:])
        self.converted_segment: AudioSegment = self.segment
        self.converted_audio_path: str = self.file_path

        self._convert_audio_to_required_format()
        log.info("Converting audio to standard format: %s", self.converted_audio_path)

    def _convert_audio_to_required_format(self):
        self._save_segment_as_wav()
        self._setup_default_params()
        os.remove(self.converted_audio_path)
        self._save_segment_as_wav()

    def _setup_default_params(self):
        from config import REQUIRED_COUNT_CHANNELS, REQUIRED_FRAME_RATE
        self.converted_segment = self.converted_segment.set_channels(channels=REQUIRED_COUNT_CHANNELS)
        self.converted_segment = self.converted_segment.set_frame_rate(frame_rate=REQUIRED_FRAME_RATE)

    def _save_segment_as_wav(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            file_path = temp_file.name
            self.converted_segment.export(file_path, format="wav")
            self.converted_audio_path = file_path
            self.converted_segment = AudioSegment.from_wav(file_path)


class Video:

    def __init__(self, file_path: str):
        self.file_path = file_path
        base, ext = os.path.splitext(file_path)
        self.extension = ext
        self.clip = VideoFileClip(self.file_path)
        audiotrack_path = self._save_audiotrack()
        self.audiotrack = Audio(audiotrack_path)

    def _save_audiotrack(self) -> str:
        audiotrack_clip = self.clip.audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            audiotrack_path = temp_file.name
            audiotrack_clip.write_audiofile(audiotrack_path, codec="pcm_s16le")
        return audiotrack_path

    def merge(self, audiotrack_path: str) -> str:
        log.debug("audiotrack_path: %s", audiotrack_path)
        audiotrack_clip = AudioFileClip(audiotrack_path)
        self.clip = self.clip.set_audio(audiotrack_clip)
        completed_video_path = self._save_video()
        return completed_video_path

    def _save_video(self) -> str:
        with tempfile.NamedTemporaryFile(suffix=self.extension, delete=False) as temp_file:
            completed_video_path = temp_file.name
            log.debug('completed_video_path: %s', completed_video_path)
            self.clip.write_videofile(completed_video_path, codec="libx264")
        return completed_video_path


class MediaSession:
    def __init__(self, file_path, sound=None, dictionary_choice=None, waiting_for_dict_file=False):
        self.file_path = file_path
        self.sound = sound
        self.dictionary_choice = dictionary_choice
        self.waiting_for_dict_file = waiting_for_dict_file
