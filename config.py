import json
from vosk import Model

MODEL_PATH = "vosk-model-small-ru-0.22"
MODEL = Model(MODEL_PATH)

REQUIRED_COUNT_CHANNELS = 1
REQUIRED_FRAME_RATE = 16000
FRAME_BLOCK_SIZE = 32000

EXTENSIONS = ['mp4', 'avi', 'mp3', 'wav', 'oga', 'ogg']
VIDEO_EXTENSIONS = ['mp4', 'mov', 'avi']
AUDIO_EXTENSIONS = ['mp3', 'wav', 'raw', 'ogg', 'oga']

with open('ban_words.json', 'r', encoding='utf-8') as f:
    forbidden_words = json.load(f)['ru_WordList']
