import telebot

api_token = input('Введите токен: ')

bot = telebot.TeleBot(api_token)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Test')


print('Bot is running.')
if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)