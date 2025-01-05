import os
from logger import ColorLogger
from media import Audio, Video
from processor import Processor

import config

processor = Processor()
log = ColorLogger(name="Media").get_logger()


def process(file_path: str, ban_words: list[str], sound: str):
    try:
        format = file_path[file_path.rindex(".") + 1:].lower()
        if format in config.VIDEO_EXTENSIONS:
            video = Video(file_path=file_path)
            converted_audio = video.convert_audio_to_required_format(
                path=video.audiotrack_path
            )
            completed_audio_path = processor.filter(
                audio_path=video.audiotrack_path,
                converted_audio_path=converted_audio.path,
                ban_words=ban_words,
                sound=sound,
            )
            completed_video_path = video.merge(
                audiotrack_path=completed_audio_path)

            return completed_video_path

        if format in config.AUDIO_EXTENSIONS:

            # if format == "oga":
            #     new_file_path = file_path
            #     new_file_path = new_file_path[:-1] + "g"
            #     new_file_path = "g" + new_file_path[1:]
            #     os.rename(file_path, new_file_path)
            #     file_path = new_file_path

            audio = Audio(file_path=file_path)
            
            converted_audio = audio.convert_audio_to_required_format(
                path=audio.file_path
            )
            completed_audio_path = processor.filter(
                audio_path=audio.file_path,
                converted_audio_path=converted_audio.path,
                ban_words=ban_words,
                sound=sound,
            )

            return completed_audio_path
        return file_path
    except Exception as e:
        log.error(e, exc_info=True)
        return file_path
