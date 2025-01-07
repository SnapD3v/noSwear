import os

from logger import ColorLogger
from process import process

log = ColorLogger(name="MediaManager").get_logger()


def process_file(file_path, replacement_sound, ban_words):
    log.info(f"Starting process for {file_path} with sound={replacement_sound}")

    result_file_path = process(file_path=file_path, ban_words=ban_words, sound_name=replacement_sound)
    return result_file_path


def generate_temp_file_name(chat_id, file_id, ext):
    return f"temp_{chat_id}_{file_id}{ext}"


def download_and_save_file(bot, file_info, chat_id):
    downloaded = bot.download_file(file_info.file_path)
    base, ext = os.path.splitext(file_info.file_path)
    ext = ext or ".ogg"
    name = generate_temp_file_name(chat_id, file_info.file_id, ext)
    with open(name, "wb") as nf:
        nf.write(downloaded)
    log.debug(f"Saved file as {name}")
    return name
