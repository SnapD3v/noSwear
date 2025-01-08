import os
import uuid

from telebot import types

from config import ALLOWED_MIME, GLOBAL_FILE_DICT, SOUNDS
from dictionary_manager import load_words_from_json, remove_custom_dictionary
from logger import ColorLogger
from media_manager import process_file, download_and_save_file
from media_session import MediaSession

log = ColorLogger(name="BotHandlers").get_logger()


def build_sounds_markup(file_short_id):
    markup = types.InlineKeyboardMarkup()
    for sound in SOUNDS:
        cb = f"SOUND|{file_short_id}|{sound}"
        markup.add(types.InlineKeyboardButton(text=sound, callback_data=cb))
    return markup


def build_dictionary_choice_markup(file_short_id):
    markup = types.InlineKeyboardMarkup()
    std = types.InlineKeyboardButton(
        text="Встроенный",
        callback_data=f"DICT_STD|{file_short_id}"
    )
    custom = types.InlineKeyboardButton(
        text="Мой",
        callback_data=f"DICT_CUSTOM|{file_short_id}"
    )
    markup.add(std, custom)
    return markup


def finalize_processing(bot, message, short_id):
    session = GLOBAL_FILE_DICT.get(short_id)
    if not session:
        log.error(f"No session found for {short_id}")
        return
    ban_words = []
    if session.dictionary_choice == "standard":
        pass
    elif session.dictionary_choice and os.path.isfile(session.dictionary_choice):
        ban_words = load_words_from_json(session.dictionary_choice)
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text="Обрабатываем..."
    )
    try:
        result_path = process_file(
            session.file_path, session.sound, ban_words=ban_words)
    except FileNotFoundError:
        log.warning(f"Result file not found for {short_id}")
        bot.send_message(
            message.chat.id, "Кто-то слишком часто нажимал кнопочки и все сломал(")
        if short_id in GLOBAL_FILE_DICT:
            del GLOBAL_FILE_DICT[short_id]
        return
    if os.path.isfile(result_path):
        with open(result_path, "rb") as rf:
            bot.send_document(message.chat.id, rf)
        os.remove(result_path)
    else:
        log.warning(f"Result file not found for {short_id}")
        bot.send_message(message.chat.id, "Файл не найден.")
    if session.dictionary_choice and os.path.isfile(session.dictionary_choice):
        remove_custom_dictionary(session.dictionary_choice)
    if short_id in GLOBAL_FILE_DICT:
        del GLOBAL_FILE_DICT[short_id]


def on_start(bot, message):
    log.info(f"Received /start from {message.chat.id}")
    bot.send_message(
        message.chat.id, "Добро пожаловать! Отправьте аудио или видео файл.")


def on_media(bot, message):
    log.info(f"Media message: {message.content_type} from {message.chat.id}")
    if message.content_type == "document" and message.document.mime_type not in ALLOWED_MIME:
        bot.send_message(message.chat.id, "Этот формат не поддерживается.")
        return
    file_id = getattr(message, message.content_type).file_id
    if not file_id:
        bot.send_message(message.chat.id, "Не удалось получить файл.")
        return
    file_info = bot.get_file(file_id)
    path = download_and_save_file(bot, file_info, message.chat.id)
    short_id = str(uuid.uuid4())
    session = MediaSession(file_path=path)
    GLOBAL_FILE_DICT[short_id] = session
    bot.send_message(
        message.chat.id,
        "Выберите звук:",
        reply_markup=build_sounds_markup(short_id)
    )


def on_document(bot, message):
    log.info(f"Document message from {message.chat.id}")
    short_id = None
    for fsid, sess in GLOBAL_FILE_DICT.items():
        if sess.waiting_for_dict_file:
            short_id = fsid
            break
    if short_id and message.document:
        if not message.document.file_name.lower().endswith(".json"):
            bot.send_message(message.chat.id, "Требуется файл *.json.")
            return
        try:
            fi = bot.get_file(message.document.file_id)
            dict_file_name = f"dict_{message.chat.id}_" \
                             f"{message.document.file_id}.json"
            downloaded = bot.download_file(fi.file_path)
            with open(dict_file_name, "wb") as f:
                f.write(downloaded)
            GLOBAL_FILE_DICT[short_id].dictionary_choice = dict_file_name
            GLOBAL_FILE_DICT[short_id].waiting_for_dict_file = False
            bot.send_message(
                message.chat.id, "Словарь загружен, обрабатываем...")
            finalize_processing(bot, message, short_id)
        except Exception as e:
            log.error(f"Error loading custom dictionary: {e}")
            bot.send_message(message.chat.id, "Ошибка при загрузке словаря.")
    else:
        bot.send_message(message.chat.id, "Этот тип не поддерживается.")


def on_unsupported(bot, message):
    log.debug(f"Unsupported content from {message.chat.id}")
    bot.send_message(
        message.chat.id, "Поддерживаются только аудио или видео файлы.")


def on_callback(bot, call):
    log.debug(f"Callback from {call.from_user.id}: {call.data}")
    parts = call.data.split("|")
    if len(parts) < 2:
        return
    action, short_id = parts[:2]
    if short_id not in GLOBAL_FILE_DICT:
        return
    if action == "SOUND":
        if len(parts) < 3:
            return
        chosen_sound = parts[2]
        GLOBAL_FILE_DICT[short_id].sound = chosen_sound
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Звук {chosen_sound} выбран. \n"
                 f"1. Встроенный словарь, содержащий русскую ненормативную лексику. \n"
                 f"2. Твой словарь в формате JSON с учётом склонений\n"
                 f"Выберите словарь:",
            reply_markup=build_dictionary_choice_markup(short_id)
        )
    elif action == "DICT_STD":
        GLOBAL_FILE_DICT[short_id].dictionary_choice = "standard"
        finalize_processing(bot, call.message, short_id)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Используем стандартный словарь, обрабатываем..."
        )
    elif action == "DICT_CUSTOM":
        GLOBAL_FILE_DICT[short_id].waiting_for_dict_file = True
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Пришлите JSON-файл со списком слов, например: [\"badword1\"]"
        )
