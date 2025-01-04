import telebot
from bot_config import BOT_TOKEN, ALLOWED_MEDIA_TYPES, ESCAPE_TYPES
from bot_handlers import on_start, on_media, on_document, on_unsupported, on_callback
from logger import ColorLogger

logger = ColorLogger(name="Main").get_logger()
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start"])
def start_cmd(message):
    on_start(bot, message)


@bot.message_handler(content_types=ALLOWED_MEDIA_TYPES)
def media_handler(message):
    on_media(bot, message)


@bot.message_handler(content_types=ESCAPE_TYPES)
def doc_handler(message):
    on_document(bot, message)


@bot.message_handler(func=lambda m: True)
def unsupported_handler(message):
    on_unsupported(bot, message)


@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    on_callback(bot, call)


if __name__ == "__main__":
    logger.info("Bot is running")
    bot.polling()
