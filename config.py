import json
from vosk import Model

MODEL_PATH = "vosk-model-ru-0.42"
MODEL = Model(MODEL_PATH)

REQUIRED_COUNT_CHANNELS = 1
REQUIRED_FRAME_RATE = 16000
FRAME_BLOCK_SIZE = 32000

EXTENSIONS = ['mp4', 'avi', 'mp3', 'wav', 'oga']

with open('ban_words.json', 'r', encoding='utf-8') as f:
    forbidden_words = json.load(f)['ru_WordList']
