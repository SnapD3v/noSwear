import os

from dotenv import load_dotenv

from media import MediaSession

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ALLOWED_MEDIA_TYPES = ["audio", "video", "video_note", "document"]
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

GLOBAL_FILE_DICT: dict[str, MediaSession] = {}

MODEL_PATH = "vosk-model-small-ru-0.22"

REQUIRED_COUNT_CHANNELS = 1
REQUIRED_FRAME_RATE = 16000
FRAME_BLOCK_SIZE = 32000

VIDEO_EXTENSIONS = ['mp4', 'mov', 'avi']
AUDIO_EXTENSIONS = ['mp3', 'wav', 'raw', 'ogg']
ALLOWED_MIME = ["audio/x-wav", "application/json"]
