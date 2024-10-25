import time

import telebot
import vosk
from telebot import types
import database as db

from process import *
from vosk import Model

import asyncio
from concurrent.futures import ThreadPoolExecutor

API_TOKEN = input('Введите токен: ')

bot = telebot.TeleBot(API_TOKEN)


# tasks = {}


# async def load_model_async(model_path=MODEL_PATH):
#     print(f'[{db.time_now()}] Начинаю загрузку модели...')
#     global model
#     # loop = asyncio.get_event_loop()
#
#     with ThreadPoolExecutor() as pool:
#         model = await asyncio.get_running_loop().run_in_executor(pool, vosk.Model, model_path)
#
#     print(f'[{db.time_now()}] Модель загружена!')
#     return model
#
#
# async def wait_for_model():
#     global model
#
#     await load_model_async()
#     return model
#
#
# async def async_processing_user_file(message):
#     user_id = message.from_user.id
#     try:
#         await wait_for_model()
#         if db.get_user_current_task(user_id, 'format') == 'Аудио':
#             process_audio_file(f'noSwear/files/non_filtered/{user_id}.wav', f'files/filtered/{user_id}.wav')
#         elif db.get_user_current_task(user_id, 'format') == 'Видео':
#             process_video_file(f'noSwear/files/non_filtered/{user_id}.mp4', f'files/filtered/{user_id}.mp4')
#             bot.send_video(message.chat.id, open(f'noSwear/files/filtered/{user_id}.mp4', 'rb'), supports_streaming=True)
#     except asyncio.CancelledError:
#         bot.send_message(message.chat.id, 'Задача была отменена')


def processing_user_file(message):
    user_id = message.from_user.id
    try:
        # await wait_for_model()
        if db.get_user_current_task(user_id, 'format') == 'Аудио':
            process_audio_file(f'noSwear/files/non_filtered/{user_id}.wav', f'noSwear/files/filtered/{user_id}.wav')
        elif db.get_user_current_task(user_id, 'format') == 'Видео':
            process_video_file(f'noSwear/files/non_filtered/{user_id}.mp4', f'noSwear/files/filtered/{user_id}.mp4')
            bot.send_video(message.chat.id, open(f'noSwear/files/filtered/{user_id}.mp4', 'rb'), supports_streaming=True)
    except Exception as e:
        db.ExceptionHandler(e)
        return


def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


available_effects = [
    'Тишина'
]


def kb_available_effects():
    kb = [types.KeyboardButton('Тишина')]
    kb_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(*kb)
    return kb_markup


@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        user_id = message.from_user.id
        if db.check_user_id_in_db(user_id):
            db.edit_user_data(user_id, 'current_task', {})
            db.clear_user_current_files(user_id)
        else:
            db.create_user_data(user_id)

        kb = [types.KeyboardButton('Видео'),
              types.KeyboardButton('Аудио')]
        kb_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(*kb)

        bot.reply_to(message,
                     '👋 Привет! Я бот “No Swear”, и я помогу очистить ваши медиафайлы. '
                     'Пожалуйста, выберите формат файла, который вы хотите обработать:',
                     reply_markup=kb_markup)
        bot.register_next_step_handler(message, file_format)
    except Exception as e:
        db.ExceptionHandler(e)
        bot.reply_to(message,
                     'Ой! Возникла какая-то ошибка... она уже была выслана разработчикам.')


@bot.message_handler(commands=['reset'])
def reset_step_handlers(message):
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id

        bot.clear_step_handler_by_chat_id(chat_id)
        db.edit_user_data(user_id, 'current_task', {})
        db.clear_user_current_files(user_id)

        if message.text == '/reset':
            bot.reply_to(message,
                         'Система успешно перезапущена, все ваши текущие задачи были сброшены.')

    except Exception as e:
        db.ExceptionHandler(e)
        bot.reply_to(message,
                     'Ой! Возникла какая-то ошибка... она уже была выслана разработчикам.')


def incorrect_message_step_handler(message, next_step_handler=None, *args):
    if message.text == '/start' or message.text == '/reset':
        reset_step_handlers(message)
        if message.text == '/start':
            send_welcome(message)
    else:
        bot.send_message(message.chat.id,
                         'Вы неверно указали ваш выбор. Пожалуйста, используйте клавиатуру в боте.')
        bot.register_next_step_handler(message, next_step_handler, *args)


def download_user_file(message, format):
    try:
        user_id = message.from_user.id
        if format == 'Аудио':
            audio_file_id = message.audio.file_id
            path = None

            if message.audio.file_name.split('.')[-1] == 'mp3':
                path = f'noSwear/files/non_filtered/{user_id}.mp3'
            elif message.audio.file_name.split('.')[-1] == 'wav':
                path = f'noSwear/files/non_filtered/{user_id}.wav'
            else:
                bot.reply_to(message,
                             'Формат вашего аудио-файла не поддерживается! Попробуйте отправить аудио-файл нужного '
                             'формата.')
                bot.register_next_step_handler(message, user_upload_file)
                return False

            if path is not None:
                bot.reply_to(message,
                             'Получил твой файл! Сейчас попробую его скачать...')

                audio_file_info = bot.get_file(audio_file_id)
                downloaded_audio_file = bot.download_file(audio_file_info.file_path)
                with open(path, 'wb') as new_audio_file:
                    new_audio_file.write(downloaded_audio_file)

                db.edit_user_current_task(user_id, 'file_exist', 'non_filtered')
                return True
            else:
                return False

        elif format == 'Видео':
            video_file_id = message.video.file_id
            path = None

            if message.video.file_name.split('.')[-1] == 'mp4':
                path = f'noSwear/files/non_filtered/{user_id}.mp4'
            else:
                bot.reply_to(message,
                             'Формат вашего видео-файла не поддерживается! Попробуйте отправить видео-файл нужного '
                             'формата.')
                bot.register_next_step_handler(message, user_upload_file)
                return False

            if path is not None:
                bot.reply_to(message,
                             'Получил твой файл! Сейчас попробую его скачать...')

                video_file_info = bot.get_file(video_file_id)
                downloaded_video_file = bot.download_file(video_file_info.file_path)
                with open(path, 'wb') as new_doc_file:
                    new_doc_file.write(downloaded_video_file)

                db.edit_user_current_task(user_id, 'file_exist', 'non_filtered')
                return True
            else:
                return False

        elif format == 'Док_Видео':
            doc_file_id = message.document.file_id
            path = f'noSwear/files/non_filtered/{user_id}.mp4'

            bot.reply_to(message,
                         'Получил твой файл! Сейчас попробую его скачать...')
            doc_file_info = bot.get_file(doc_file_id)
            downloaded_doc_file = bot.download_file(doc_file_info.file_path)
            with open(path, 'wb') as new_doc_file:
                new_doc_file.write(downloaded_doc_file)

            db.edit_user_current_task(user_id, 'file_exist', 'non_filtered')
            return True

        elif format == 'Док_Аудио':
            doc_file_id = message.document.file_id
            path = None

            if message.document.file_name.split('.')[-1] == 'mp3':
                path = f'noSwear/files/non_filtered/{user_id}.mp3'
            elif message.document.file_name.split('.')[-1] == 'wav':
                path = f'noSwear/files/non_filtered/{user_id}.wav'

            if path is not None:
                bot.reply_to(message,
                             'Получил твой файл! Сейчас попробую его скачать...')
                doc_file_info = bot.get_file(doc_file_id)
                downloaded_doc_file = bot.download_file(doc_file_info.file_path)
                with open(path, 'wb') as new_doc_file:
                    new_doc_file.write(downloaded_doc_file)

                db.edit_user_current_task(user_id, 'file_exist', 'non_filtered')
                return True
            else:
                return False
    except Exception as e:
        db.ExceptionHandler(e)
        return False


# Ниже начинается цикл взаимодействия бота с пользователем
def file_format(message):
    try:
        user_id = message.from_user.id

        if message.text == 'Видео' or message.text == 'Аудио':
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
    except Exception as e:
        db.ExceptionHandler(e)
        bot.reply_to(message,
                     'Ой! Возникла какая-то ошибка... она уже была выслана разработчикам.')


def words_to_change(message):
    try:
        user_id = message.from_user.id

        if message.text == 'Нецензурную лексику (русский)':
            db.edit_user_current_task(user_id, 'ban_list', 'default')

            kb_markup = kb_available_effects()

            bot.reply_to(message,
                         'Пожалуйста, выберите, на что заменить эти слова:',
                         reply_markup=kb_markup)
            bot.register_next_step_handler(message, change_effect)

        elif message.text == 'Самостоятельный выбор слов':
            db.edit_user_current_task(user_id, 'ban_list', 'own')

            bot.reply_to(message,
                         'Введите слова, которые хотите заменить, через запятую.')
            bot.register_next_step_handler(message, set_own_word_list)

        else:
            incorrect_message_step_handler(message, words_to_change)
    except Exception as e:
        db.ExceptionHandler(e)
        bot.reply_to(message,
                     'Ой! Возникла какая-то ошибка... она уже была выслана разработчикам.')


def set_own_word_list(message):
    try:
        if message.text == '/start' or message.text == '/reset':
            incorrect_message_step_handler(message)
        else:
            word_list = message.text.split(',')

            kb = [types.KeyboardButton('Да'),
                  types.KeyboardButton('Нет')]
            kb_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(*kb)

            bot.reply_to(message,
                         f'Вы выбрали следующие слова, которые будут заменены: \n{" | ".join(word_list)} \nВерно?',
                         reply_markup=kb_markup)
            bot.register_next_step_handler(message, confirm_set_own_word_list, word_list)
    except Exception as e:
        db.ExceptionHandler(e)
        bot.reply_to(message,
                     'Ой! Возникла какая-то ошибка... она уже была выслана разработчикам.')


def confirm_set_own_word_list(message, word_list):
    try:
        user_id = message.from_user.id

        if message.text == 'Да':
            db.edit_user_current_task(user_id, 'word_list', word_list)
            kb_markup = kb_available_effects()

            bot.reply_to(message,
                         'Пожалуйста, выберите, на что заменить эти слова:',
                         reply_markup=kb_markup)
            bot.register_next_step_handler(message, change_effect)

        elif message.text == 'Нет':
            db.edit_user_current_task(user_id, 'word_list', '')

            bot.reply_to(message,
                         'Введите слова, которые хотите заменить, через запятую.')
            bot.register_next_step_handler(message, set_own_word_list)
        else:
            incorrect_message_step_handler(message, confirm_set_own_word_list, word_list)
    except Exception as e:
        db.ExceptionHandler(e)
        bot.reply_to(message,
                     'Ой! Возникла какая-то ошибка... она уже была выслана разработчикам.')


def change_effect(message):
    try:
        user_id = message.from_user.id
        if message.text in available_effects:
            db.edit_user_current_task(user_id, 'effect', message.text)

            message_text = f'Отлично! Теперь пришло время загрузить ваш ' \
                           f'{db.get_user_current_task(user_id, "format")} файл для обработки. \n' \
                           'Пожалуйста, отправьте файл, который вы хотите очистить от нецензурной лексики. \n\n' \
                           'Убедитесь, что файл соответствует следующим требованиям: \n'
            if db.get_user_current_task(user_id, "format") == "Аудио":
                message_text += 'Формат: .mp3 / .wav\nПосле загрузки я начну обработку!'
            else:
                message_text += 'Формат: .mp4\nПосле загрузки я начну обработку!'

            bot.reply_to(message, message_text)
            bot.register_next_step_handler(message, user_upload_file)
        else:
            incorrect_message_step_handler(message, change_effect)

    except Exception as e:
        db.ExceptionHandler(e)
        bot.reply_to(message,
                     'Ой! Возникла какая-то ошибка... она уже была выслана разработчикам.')


def user_upload_file(message):
    user_id = message.from_user.id
    flag = False

    try:
        if message.text == '/start' or message.text == '/reset':
            incorrect_message_step_handler(message)
            return
        if db.get_user_current_task(user_id, 'format') == 'Аудио' and message.content_type == 'audio':
            flag = download_user_file(message, 'Аудио')
        elif db.get_user_current_task(user_id, 'format') == 'Видео' and message.content_type == 'video':
            flag = download_user_file(message, 'Видео')
        elif message.content_type == 'document':
            if db.get_user_current_task(user_id, 'format') == 'Видео' and \
                    message.document.file_name.split('.')[-1] == 'mp4':
                flag = download_user_file(message, 'Док_Видео')
            elif db.get_user_current_task(user_id, 'format') == 'Аудио' and \
                    (message.document.file_name.split('.')[-1] == 'mp3' or message.document.file_name.split('.')[
                        -1] == 'wav'):
                flag = download_user_file(message, 'Док_Аудио')
        else:
            bot.reply_to(message,
                         'Формат вашего файла не поддерживается! Попробуйте отправить файл нужного формата.')
            bot.register_next_step_handler(message, user_upload_file)
            return

        if flag:
            bot.reply_to(message,
                         '✅ Файл успешно загружен! Я начинаю обработку. \n'
                         '⏳ Это может занять некоторое время, в зависимости от размера файла. \n'
                         'Пожалуйста, подождите. Когда обработка завершится, я отправлю вам очищенную '
                         'версию файла.')
            processing_user_file(message)
    except Exception as e:
        db.ExceptionHandler(e)
        bot.reply_to(message,
                     'Возникла ошибка!')


print('Bot is running.')

bot.enable_save_next_step_handlers(delay=1)

bot.load_next_step_handlers()


# async def main():
#     await asyncio.gather(*(bot_polling(), vosk_process()))


# async def bot_polling():
#     bot.polling(none_stop=True, interval=0)


# async def vosk_process():
#     if model is None:
#         loop = asyncio.get_event_loop()
#         task = loop.create_task(load_model_async())


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        db.ExceptionHandler(e)
    # while True:
    #     try:
    #         # asyncio.run(main())
    #         bot.polling(none_stop=True, interval=0)
    #
    #     except Exception as e:
    #         db.ExceptionHandler(e)
    #         time.sleep(5)
    #         continue
    #     finally:
    #         # for user_id in tasks:
    #         #     tasks[user_id].cancel()
    #         #     del tasks[user_id]
    #         for user_id in db.open_db():
    #             db.edit_user_data(user_id, 'current_task', {})
    #             db.clear_user_current_files(user_id)
    #         print(f'[{db.time_now()}] Все задачи остановлены')
