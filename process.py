from media import Audio, Video
from processor import Processor

processor = Processor()


def process(format: str, file_path: str, ban_words: list[str], sound: str):

    if format == 'Видео':
        video = Video(file_path=file_path)
        converted_audio = video.convert_audio_to_required_format(path=video.audiotrack_path)
        complited_audio_path = processor.filter(
            audio_path=video.audiotrack_path,
            converted_audio_path=converted_audio.path,
            ban_words=ban_words,
            sound=sound
            )
        complited_video_path = video.merge(audiotrack_path=complited_audio_path)

        return complited_video_path

    if format == 'Аудио':
        audio = Audio(file_path=file_path)
        converted_audio = audio.convert_audio_to_required_format(path=audio.file_path)
        complited_audio_path = processor.filter(
            audio_path=audio.file_path,
            converted_audio_path=converted_audio.path,
            ban_words=ban_words,
            sound=sound
            )

        return complited_audio_path
