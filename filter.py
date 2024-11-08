from config import *

from vosk import KaldiRecognizer, SetLogLevel
from pydub import AudioSegment
from typing import List
import tempfile
import json
import wave
import os

SetLogLevel(0)


def convert_audio_to_required_format(origin_audio_file_path: str) -> str:

    audio_for_recognizer = AudioSegment.from_file(origin_audio_file_path)
    audio_for_recognizer = audio_for_recognizer.set_channels(REQUIRED_COUNT_CHANNELS)
    audio_for_recognizer = audio_for_recognizer.set_frame_rate(REQUIRED_FRAME_RATE)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file_for_recognizer:

        audio_file_path = temp_file_for_recognizer.name
        audio_for_recognizer.export(audio_file_path, format="wav")

    return audio_file_path


def get_timestamps(audio_file_path: str) -> List[dict]:

    with wave.open(audio_file_path, "rb") as wave_audio_file:

        recognizer = KaldiRecognizer(MODEL, REQUIRED_FRAME_RATE)
        recognizer.SetWords(True)

        while True:

            data = wave_audio_file.readframes(FRAME_BLOCK_SIZE)

            if len(data) == 0:
                break

            recognizer.AcceptWaveform(data)

    timestamps = json.loads(recognizer.FinalResult())

    if "result" in timestamps:
        return timestamps["result"]

    return []


def get_timestamps_for_filtering(timestamps: List[dict]) -> List[dict]:

    timestamps_for_filtering = []

    for word_info in timestamps:

        if word_info["word"] in forbidden_words:
            timestamps_for_filtering.append(
                {
                    "word": word_info["word"],
                    "start": word_info["start"] * 1000,
                    "end": word_info["end"] * 1000
                })

    return timestamps_for_filtering


def filter_audio_file(audio_file_path: str) -> AudioSegment:

    path_converted_audio = convert_audio_to_required_format(audio_file_path)

    timestamps = get_timestamps(path_converted_audio)
    timestamps_for_filtering = get_timestamps_for_filtering(timestamps)

    os.remove(path_converted_audio)

    audio_segment = AudioSegment.from_file(audio_file_path)

    if not timestamps_for_filtering:
        return audio_segment

    new_audio_segment = audio_segment[:timestamps_for_filtering[0]['start']]

    for i, word in enumerate(timestamps_for_filtering):
        silence_duration = (word['end'] - word['start'])
        new_audio_segment += AudioSegment.silent(duration=silence_duration)

        if i == len(timestamps_for_filtering) - 1:
            new_audio_segment += audio_segment[timestamps_for_filtering[-1]['end']:]
            return new_audio_segment

        new_audio_segment += audio_segment[word['end']:timestamps_for_filtering[i + 1]['start']]
