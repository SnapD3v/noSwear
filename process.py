from media import Audio, Video
from processor import Processor

processor = Processor()


def process(file_format: str, file_path: str, ban_words: list[str], sound: str):
    if file_format == 'Видео':
        video = Video(file_path=file_path)
        converted_audio = video.convert_audio_to_required_format(path=video.audiotrack_path)
        completed_audio_path = processor.filter(
            audio_path=video.audiotrack_path,
            converted_audio_path=converted_audio.path,
            ban_words=ban_words,
            sound=sound
        )
        completed_video_path = video.merge(audiotrack_path=completed_audio_path)

        return completed_video_path

    if file_format == 'Аудио':
        audio = Audio(file_path=file_path)
        converted_audio = audio.convert_audio_to_required_format(path=audio.file_path)
        completed_audio_path = processor.filter(
            audio_path=audio.file_path,
            converted_audio_path=converted_audio.path,
            ban_words=ban_words,
            sound=sound
        )

        return completed_audio_path
