from filter import *

from moviepy.editor import VideoFileClip, AudioFileClip


def process_audio_file(input_audio_file_path: str, output_audio_file_path: str) -> None:
    new_audio_file = filter_audio_file(input_audio_file_path)

    new_audio_file.export(output_audio_file_path, format="wav")


def process_video_file(input_video_file_path: str, output_video_file_path: str) -> None:
    audio_file_path = get_audio_from_video(input_video_file_path)

    new_audio_file = filter_audio_file(audio_file_path)
    new_audio_file.export(audio_file_path, format="wav")

    new_video_file = VideoFileClip(input_video_file_path).set_audio(AudioFileClip(audio_file_path))
    new_video_file.write_videofile(output_video_file_path)

    os.remove(audio_file_path)


def get_audio_from_video(video_file_path: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        audio_file_clip = VideoFileClip(video_file_path).audio
        temp_file_path = temp_file.name        
        audio_file_clip.write_audiofile(temp_file_path, codec="pcm_s16le")
    
    return temp_file_path
