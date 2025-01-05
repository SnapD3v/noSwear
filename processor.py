import json
import os
from pydub import AudioSegment
import tempfile
from vosk import KaldiRecognizer, Model, SetLogLevel
import wave

import config

SetLogLevel(0)


class Processor:
    """Обработчик аудиофайлов"""

    def __init__(self):
        self.model = Model(config.MODEL_PATH)

    def filter(
        self,
        audio_path: str,
        converted_audio_path: str,
        ban_words: list[str],
        sound: str,
    ) -> str:
        timestamps: list[dict] = self._get_timestamps_for_filtering(
            converted_audio_path, ban_words
        )
        os.remove(converted_audio_path)

        audio_segment = AudioSegment.from_file(audio_path)
        if not timestamps:
            return audio_segment

        new_audio_segment = audio_segment[: timestamps[0]["start"]]

        for i, word in enumerate(timestamps):
            sound_duration = word["end"] - word["start"]
            if sound == "Тишина":
                new_audio_segment += AudioSegment.silent(duration=sound_duration)
            elif sound == "Дельфин":
                pass
            elif sound == "Кря":
                pass
            elif sound == "Пик":
                pass

            if i == len(timestamps) - 1:
                new_audio_segment += audio_segment[timestamps[-1]["end"] :]
                suffix = audio_path[audio_path.rindex(".") + 1 :]
                completed_audio_path = self._save_segment(
                    audio_segment=new_audio_segment, suffix=suffix
                )
                break

            new_audio_segment += audio_segment[word["end"] : timestamps[i + 1]["start"]]
        return completed_audio_path

    def _get_timestamps_for_filtering(
        self,
        file_path: str,
        ban_words: list[str]
    ) -> list[dict]:
        timestamps = self._get_timestamps(file_path)
        timestamps_for_filtering = []

        for word_info in timestamps:
            if word_info["word"] in ban_words:
                timestamps_for_filtering.append(
                    {
                        "word": word_info["word"],
                        "start": word_info["start"] * 1000,
                        "end": word_info["end"] * 1000,
                    }
                )

        return timestamps_for_filtering

    def _get_timestamps(self, file_path: str) -> list[dict]:
        with wave.open(file_path, "rb") as wave_file:
            recognizer = KaldiRecognizer(self.model, config.REQUIRED_FRAME_RATE)
            recognizer.SetWords(True)
            while True:
                data = wave_file.readframes(config.FRAME_BLOCK_SIZE)
                if len(data) == 0:
                    break
                recognizer.AcceptWaveform(data)

            final_result = json.loads(recognizer.FinalResult())

        if "result" in final_result:
            timestamps = final_result["result"]
            return timestamps
        return []

    def _save_segment(self, audio_segment: AudioSegment, suffix: str) -> str:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            completed_audio_path = temp_file.name
            audio_segment.export(completed_audio_path, format=suffix)
        return completed_audio_path
