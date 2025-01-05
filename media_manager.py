import os

from logger import ColorLogger
from process import process

log = ColorLogger(name="MediaManager").get_logger()


def process_file(file_path, replacement_sound, words_list):
    log.info(f"Starting process for {file_path} with sound={replacement_sound}")
    log.debug(f"Words list: {words_list}")

    file_path = process(file_format="", file_path=file_path, ban_words=words_list, sound=replacement_sound)
    return file_path


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
