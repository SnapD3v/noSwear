import time

from process import *
import database as db

import telebot
from telebot import types

API_TOKEN = open("token.txt", "r").readline()

bot = telebot.TeleBot(API_TOKEN)


def ExceptionHandler(exception, message=None):
    """Error handling function."""
    print(f'\n---\n'
          f'[{db.time_now()}] Возникла ошибка! [bot.py]\n'
          f'[Type]: {type(exception)}\n'
          f'[Exception Context]: {exception.__context__}\n'
          f'[Exception Cause]: {exception.__cause__}\n'
          f'[Exception Suppress Context]: {exception.__suppress_context__}\n'
          f'[UserID]: {message.from_user.id}\n'
          f'[Text]: {message.text}\n'
          f'---\n')
    if message is not None:
        bot.send_message(chat_id=message.chat.id,
                         text='Возникла ошибка! Она уже была передана разработчикам.')


@bot.message_handler(commands=['reset'])
def reset_step_handlers(message):
    """Function to reset the current user task. ( /reset )"""
    try:
        user_id: int = message.from_user.id
        chat_id: int = message.chat.id

        bot.clear_step_handler_by_chat_id(chat_id)
        db.reset_user_task(user_id)

        if message.text == '/reset':
            bot.reply_to(message, 'Система успешно перезапущена, все ваши текущие задачи были сброшены.')

    except Exception as error:
        ExceptionHandler(error, message)


def incorrect_message_step_handler(message, next_step_handler=None, *args):
    """Incorrect input handling function for step_handlers."""
    try:
        if message.text in ('/start', '/reset'):
            reset_step_handlers(message)
            if message.text == '/start':
                send_welcome(message)
        else:
            bot.send_message(message.chat.id,
                             'Вы неверно указали ваш выбор. Пожалуйста, используйте клавиатуру в боте.')
            bot.register_next_step_handler(message, next_step_handler, *args)

    except Exception as error:
        ExceptionHandler(error, message)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """(1) The initial function of the /start command, which starts the interaction process from the beginning."""
    try:
        user_id: int = message.from_user.id
        db.reset_user_task(user_id) if db.check_user_id_in_db(user_id) else db.create_user_data(user_id)

        kb = [types.KeyboardButton('Видео'),
              types.KeyboardButton('Аудио')]
        kb_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(*kb)

        bot.reply_to(message,
                     '👋 Привет! Я бот “No Swear”, и я помогу очистить ваши медиафайлы. '
                     'Пожалуйста, выберите формат файла, который вы хотите обработать:',
                     reply_markup=kb_markup)
        bot.register_next_step_handler(message, file_format)

    except Exception as error:
        ExceptionHandler(error, message)


def file_format(message):
    """(2) Step_handler function for selecting the format of the future user file."""
    try:
        user_id: int = message.from_user.id

        if message.text in ('Видео', 'Аудио'):
            db.edit_user_current_task(user_id, 'format', message.text)

            kb = [types.KeyboardButton('Нецензурную лексику (русский)'),
                  types.KeyboardButton('Самостоятельный выбор слов')]
            kb_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(*kb)

            bot.reply_to(message,
                         'Отлично! Теперь давайте определим, что именно нужно заменить. \n\n'
                         'Пожалуйста, выберите один из вариантов: \n'
                         '1. Заменить нецензурную лексику (только на русском языке) \n'
                         '2. Самостоятельный выбор слов',
                         reply_markup=kb_markup)
            bot.register_next_step_handler(message, words_to_change)
        else:
            incorrect_message_step_handler(message, file_format)

    except Exception as error:
        ExceptionHandler(error, message)


def words_to_change(message):
    """(3) Step_handler function for selecting a dictionary of forbidden words."""
    try:
        user_id: int = message.from_user.id

        if message.text == 'Нецензурную лексику (русский)':
            db.edit_user_current_task(user_id, 'ban_list', 'default')

            if db.is_exist_user_task_detail(user_id, 'file_path'):
                check_all_details(message)
            else:
                message_text = f'Отлично! Теперь пришло время загрузить ваш ' \
                               f'{db.get_user_task_detail(user_id, "format")} файл для обработки. \n' \
                               'Пожалуйста, отправьте файл, который вы хотите очистить от нецензурной лексики. \n\n' \
                               'Убедитесь, что файл соответствует следующим требованиям: \n'
                if db.get_user_task_detail(user_id, "format") == "Аудио":
                    message_text += 'Формат: .wav\nПосле загрузки я начну обработку!'
                else:
                    message_text += 'Формат: .mp4\nПосле загрузки я начну обработку!'

                bot.reply_to(message, message_text)
                bot.register_next_step_handler(message, user_upload_file)

        elif message.text == 'Самостоятельный выбор слов':
            db.edit_user_current_task(user_id, 'ban_list', 'own')

            bot.reply_to(message,
                         'Введите слова, которые хотите заменить:')
            bot.register_next_step_handler(message, set_own_word_list)

        else:
            incorrect_message_step_handler(message, words_to_change)

    except Exception as error:
        ExceptionHandler(error, message)


def set_own_word_list(message):
    """(3.1) Step_handler function for self-selection of forbidden words."""
    try:
        if message.text in ('/start', '/reset'):
            incorrect_message_step_handler(message)
        else:
            word_list = [word.replace(',', '').lower() for word in message.text.split(' ')]
            kb = [types.KeyboardButton('Да'),
                  types.KeyboardButton('Нет')]
            kb_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(*kb)

            bot.reply_to(message,
                         f'Вы выбрали следующие слова, которые будут заменены: \n{" | ".join(word_list)} \nВерно?',
                         reply_markup=kb_markup)
            bot.register_next_step_handler(message, confirm_set_own_word_list, word_list)

    except Exception as error:
        ExceptionHandler(error, message)


def confirm_set_own_word_list(message, word_list):
    """(4) Step_handler function to approve the dictionary of forbidden words."""
    try:
        user_id: int = message.from_user.id

        if message.text == 'Да':
            db.edit_user_current_task(user_id, 'word_list', word_list)
            if db.is_exist_user_task_detail(user_id, 'file_path'):
                check_all_details(message)
            else:
                message_text = f'Отлично! Теперь пришло время загрузить ваш ' \
                               f'{db.get_user_task_detail(user_id, "format")} файл для обработки. \n' \
                               'Пожалуйста, отправьте файл, который вы хотите очистить от нецензурной лексики. \n\n' \
                               'Убедитесь, что файл соответствует следующим требованиям: \n'
                if db.get_user_task_detail(user_id, "format") == "Аудио":
                    message_text += 'Формат: .wav\nПосле загрузки я начну обработку!'
                else:
                    message_text += 'Формат: .mp4\nПосле загрузки я начну обработку!'

                bot.reply_to(message, message_text)
                bot.register_next_step_handler(message, user_upload_file)

        elif message.text == 'Нет':
            db.edit_user_current_task(user_id, 'word_list', '')

            bot.reply_to(message,
                         'Введите слова, которые хотите заменить.')
            bot.register_next_step_handler(message, set_own_word_list)
        else:
            incorrect_message_step_handler(message, confirm_set_own_word_list, word_list)

    except Exception as error:
        ExceptionHandler(error, message)


def user_upload_file(message):
    """(5) Step_handler outer shell function for downloading a user file into the project directory."""
    user_id: int = message.from_user.id
    flag: bool = False

    try:
        if message.text in ('/start', '/reset'):
            incorrect_message_step_handler(message)

        if db.get_user_task_detail(user_id, 'format') == 'Аудио' and message.content_type == 'audio' and \
                message.audio.file_name.split('.')[-1].lower() in EXTENSIONS:
            flag = download_user_file(message, 'Аудио')

        elif db.get_user_task_detail(user_id, 'format') == 'Видео' and message.content_type == 'video' and \
                message.video.file_name.split('.')[-1].lower() in EXTENSIONS:
            flag = download_user_file(message, 'Видео')

        elif message.content_type == 'document':
            print(f'[{db.time_now()}] {user_id} - sent file "{message.document.file_name}" - doc recieved')
            file_extension = message.document.file_name.split('.')[-1].lower()
            if db.get_user_task_detail(user_id, 'format') == 'Видео' and file_extension in EXTENSIONS:
                flag = download_user_file(message, 'Док_Видео')
            elif db.get_user_task_detail(user_id, 'format') == 'Аудио' and file_extension in EXTENSIONS:
                flag = download_user_file(message, 'Док_Аудио')

        else:
            bot.reply_to(message,
                         'Формат вашего файла не поддерживается! Попробуйте отправить файл нужного формата.')
            bot.register_next_step_handler(message, user_upload_file)

        if flag:
            check_all_details(message)

    except Exception as error:
        ExceptionHandler(error, message)


def check_all_details(message):
    """Function for user approval of all file processing settings."""
    user_id: int = message.from_user.id

    kb = [types.KeyboardButton('Обработать'),
          types.KeyboardButton('Слова')]
    kb_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(*kb)

    if db.get_user_task_detail(user_id, 'ban_list') == 'own':
        word_list = ', '.join(db.get_user_task_detail(user_id, 'word_list'))
    else:
        word_list = 'Автоматический'
    bot.reply_to(message=message,
                 text=f'✅ Файл успешно загружен! Проверьте все настройки перед началом обработки:\n'
                      f'Формат файла: {db.get_user_task_detail(user_id, "format")}\n'
                      f'Расширение файла: {db.get_user_task_detail(user_id, "file_extension")}\n'
                      f'Список запрещенных слов: {word_list}',
                 reply_markup=kb_markup)
    bot.register_next_step_handler(message, confirm_user_task)


def download_user_file(message, file_type):
    """Function for uploading a user file"""
    try:
        user_id: int = message.from_user.id
        path = f'files/non_filtered/{user_id}'

        if file_type == 'Аудио':
            audio_file_id = message.audio.file_id

            print(f'[{db.time_now()}] {user_id} - sent file "{message.audio.file_name}" - audio recieved')
            file_extension = '.' + message.audio.file_name.split('.')[-1].lower()
            db.edit_user_current_task(user_id, 'file_extension', file_extension)
            path += file_extension

            bot.reply_to(message,
                         'Получил твой файл! Сейчас попробую его скачать...')

            audio_file_info = bot.get_file(audio_file_id)
            downloaded_audio_file = bot.download_file(audio_file_info.file_path)
            with open(path, 'wb') as new_audio_file:
                new_audio_file.write(downloaded_audio_file)

            db.edit_user_current_task(user_id, 'file_path', 'files/non_filtered/')
            return True

        elif file_type == 'Видео':
            video_file_id = message.video.file_id

            print(f'[{db.time_now()}] {user_id} - sent file "{message.video.file_name}" - video recieved')
            file_extension = '.' + message.video.file_name.split('.')[-1].lower()
            db.edit_user_current_task(user_id, 'file_extension', file_extension)
            path += file_extension

            bot.reply_to(message,
                         'Получил твой файл! Сейчас попробую его скачать...')

            video_file_info = bot.get_file(video_file_id)
            downloaded_video_file = bot.download_file(video_file_info.file_path)
            with open(path, 'wb') as new_doc_file:
                new_doc_file.write(downloaded_video_file)

            db.edit_user_current_task(user_id, 'file_path', 'files/non_filtered/')
            return True

        elif file_type == 'Док_Видео':
            doc_file_id = message.document.file_id

            print(f'[{db.time_now()}] {user_id} - sent file "{message.document.file_name}" - video doc recieved')
            file_extension = '.' + message.document.file_name.split('.')[-1].lower()
            db.edit_user_current_task(user_id, 'file_extension', file_extension)
            path += file_extension

            bot.reply_to(message,
                         'Получил твой файл! Сейчас попробую его скачать...')
            doc_file_info = bot.get_file(doc_file_id)
            downloaded_doc_file = bot.download_file(doc_file_info.file_path)
            with open(path, 'wb') as new_doc_file:
                new_doc_file.write(downloaded_doc_file)

            db.edit_user_current_task(user_id, 'file_path', 'files/non_filtered')
            return True

        elif file_type == 'Док_Аудио':
            doc_file_id = message.document.file_id

            print(f'[{db.time_now()}] {user_id} - sent file "{message.document.file_name}" - audio doc recieved')
            file_extension = '.' + message.document.file_name.split('.')[-1].lower()
            db.edit_user_current_task(user_id, 'file_extension', file_extension)
            path += file_extension

            bot.reply_to(message,
                         'Получил твой файл! Сейчас попробую его скачать...')
            doc_file_info = bot.get_file(doc_file_id)
            downloaded_doc_file = bot.download_file(doc_file_info.file_path)
            with open(path, 'wb') as new_doc_file:
                new_doc_file.write(downloaded_doc_file)

            db.edit_user_current_task(user_id, 'file_path', 'files/non_filtered')
            return True
    except Exception as error:
        ExceptionHandler(error, message)


def confirm_user_task(message):
    """(6) Step_handler function to confirm the start of user file processing."""
    try:
        if message.text == 'Обработать':
            bot.reply_to(message,
                         'Я начинаю обработку. \n'
                         '⏳ Это может занять некоторое время, в зависимости от размера файла. \n'
                         'Пожалуйста, подождите. Когда обработка завершится, я отправлю вам очищенную '
                         'версию файла.')
            processing_user_file(message)

        elif message.text == 'Слова':
            kb = [types.KeyboardButton('Нецензурную лексику (русский)'),
                  types.KeyboardButton('Самостоятельный выбор слов')]
            kb_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(*kb)

            bot.reply_to(message,
                         'Давайте определим, что именно нужно заменить. \n\n'
                         'Пожалуйста, выберите один из вариантов: \n'
                         '1. Заменить нецензурную лексику (только на русском языке) \n'
                         '2. Самостоятельный выбор слов',
                         reply_markup=kb_markup)
            bot.register_next_step_handler(message, words_to_change)

        else:
            incorrect_message_step_handler(message, confirm_user_task)

    except Exception as error:
        ExceptionHandler(error, message)


def processing_user_file(message):
    """(7) Step_handler function to process a user file."""
    user_id: int = message.from_user.id
    try:
        user_file_extension = db.get_user_task_detail(user_id, 'file_extension')
        if db.get_user_task_detail(user_id, 'ban_list') == 'own':
            word_list = db.get_user_task_detail(user_id, 'word_list')
        else:
            word_list = forbidden_words
        if db.get_user_task_detail(user_id, 'format') == 'Аудио':
            process_audio_file(input_audio_file_path=f'files/non_filtered/{user_id}{user_file_extension}',
                               output_audio_file_path=f'files/filtered/{user_id}.wav',
                               word_list=word_list)

            bot.send_audio(message.chat.id,
                           audio=open(f'files/filtered/{user_id}.wav', 'rb'),
                           caption='✅ Файл успешно обработан!')

            db.clear_user_current_files(user_id, 'filtered')
            db.clear_user_current_files(user_id, 'non_filtered')

        elif db.get_user_task_detail(user_id, 'format') == 'Видео':
            process_video_file(input_video_file_path=f'files/non_filtered/{user_id}{user_file_extension}',
                               output_video_file_path=f'files/filtered/{user_id}{user_file_extension}',
                               word_list=word_list)

            bot.send_video(message.chat.id,
                           open(f'files/filtered/{user_id}{user_file_extension}', 'rb'),
                           caption='✅ Файл успешно обработан!',
                           supports_streaming=True)

            db.clear_user_current_files(user_id, 'filtered')
            db.clear_user_current_files(user_id, 'non_filtered')

    except Exception as error:
        ExceptionHandler(error, message)


print('Bot is running.')

bot.enable_save_next_step_handlers(delay=1)

bot.load_next_step_handlers()  # Подгрузка step_handlers при перезагрузке бота


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            db.ExceptionHandler(e)
            time.sleep(5)
            continue

        # finally:
        #     for user_id in db.open_db():
        #         db.edit_user_data(user_id, 'current_task', {})
        #         db.clear_user_current_files(user_id, 'filtered')
        #         db.clear_user_current_files(user_id, 'non_filtered')
        #     print(f'[{db.time_now()}] Все задачи остановлены')
