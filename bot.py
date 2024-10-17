import telebot
from telebot import types
import database as db

api_token = input('Введите токен: ')

bot = telebot.TeleBot(api_token)


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

            bot.reply_to(message,
                         'Отлично! Теперь пришло время загрузить ваш [видео/аудио] файл для обработки. \n'
                         'Пожалуйста, отправьте файл, который вы хотите очистить от нецензурной лексики. \n\n'
                         'Убедитесь, что файл соответствует следующим требованиям: \n'
                         'Формат: .mp4 / .mp3 / .wav\n'
                         'После загрузки я начну обработку!')
            bot.register_next_step_handler(message, user_upload_file)
        else:
            incorrect_message_step_handler(message, change_effect)

    except Exception as e:
        db.ExceptionHandler(e)
        bot.reply_to(message,
                     'Ой! Возникла какая-то ошибка... она уже была выслана разработчикам.')


def user_upload_file(message):
    bot.reply_to(message,
                 'Тест завершен :)')


def bot_error_handler(e):
    pass


print('Bot is running.')

bot.enable_save_next_step_handlers(delay=1)

bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)