import json
from vosk import Model

MODEL_PATH = "noSwear/vosk-model-ru-0.42"
print('Начинаю загрузку модели...')
MODEL = Model(MODEL_PATH) # нужно сделать так чтоб это запускалось отдельно, сразу с ботом

# FORMAT = 'видео'

# INPUT_VIDEO_FILE_PATH = r"raw-media\video5470164889005742920.mp4"
# INPUT_AUDIO_FILE_PATH = r"raw-media\input_audio.wav"

# OUTPUT_VIDEO_FILE_PATH = r"output-media\output_video.mp4"
# OUTPUT_AUDIO_FILE_PATH = r"output-media\output_audio.wav"

REQUIRED_COUNT_CHANNELS = 1
REQUIRED_FRAME_RATE = 16000
FRAME_BLOCK_SIZE = 32000

with open('noSwear/ban_words.json', 'r', encoding='utf-8') as f:
    forbidden_words = json.load(f)['ru_WordList']