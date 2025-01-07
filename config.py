import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ALLOWED_MEDIA_TYPES = ["audio", "video", "video_note"]
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
    "any_other_types_etc",
    "voice"
]
SOUNDS = ["Тишина", "Дельфин", "Кря", "Пароход", "Пик"]

GLOBAL_FILE_DICT = {}


MODEL_PATH = "vosk-model-small-ru-0.22"

REQUIRED_COUNT_CHANNELS = 1
REQUIRED_FRAME_RATE = 16000
FRAME_BLOCK_SIZE = 32000

VIDEO_EXTENSIONS = ['mp4', 'mov', 'avi']
AUDIO_EXTENSIONS = ['mp3', 'wav', 'raw', 'ogg']
