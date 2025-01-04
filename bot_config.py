import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ALLOWED_MEDIA_TYPES = ["audio", "voice", "video", "video_note"]
ESCAPE_TYPES = [
    "document",
    "photo",
    "sticker",
    "location",
    "contact",
    "poll",
    "dice",
    "venue",
    "animation",
    "any_other_types_etc"
]
GLOBAL_FILE_DICT = {}
