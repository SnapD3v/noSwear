import os
from logger import ColorLogger
from media import Audio, Video
from processor import Processor

from config import AUDIO_EXTENSIONS, VIDEO_EXTENSIONS

processor = Processor()
log = ColorLogger(name="Media").get_logger()


def process(file_path: str, ban_words: list[str], sound_name: str):
    try:
        extension = file_path[file_path.rindex(".") + 1:].lower()
        if extension in VIDEO_EXTENSIONS:
            video = Video(file_path=file_path)
            completed_audio_path = processor.filter(
                audio=video.audiotrack,
                ban_words=ban_words,
                sound_name=sound_name,
            )
            completed_video_path = video.merge(audiotrack_path=completed_audio_path)
            os.remove(completed_audio_path)
            os.remove(video.file_path)
            os.remove(video.audiotrack.file_path)
            os.remove(video.audiotrack.converted_audio_path)
            return completed_video_path

        if extension in AUDIO_EXTENSIONS:
            audio = Audio(file_path=file_path)
            completed_audio_path = processor.filter(
                audio=audio,
                ban_words=ban_words,
                sound_name=sound_name,
            )
            log.debug('Completed path: %s', completed_audio_path)
            os.remove(audio.file_path)
            os.remove(audio.converted_audio_path)
            return completed_audio_path
        return file_path

    except Exception as e:
        log.error(e, exc_info=True)
        return file_path
