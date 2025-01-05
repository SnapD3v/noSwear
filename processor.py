import json
from pydub import AudioSegment
import tempfile
from vosk import KaldiRecognizer, Model, SetLogLevel
import wave

import config
from logger import ColorLogger
from media import Audio

SetLogLevel(0)
log = ColorLogger(name="Processor").get_logger()


class Processor:
    """Обработчик аудиофайлов"""

    def __init__(self):
        self.model = Model(config.MODEL_PATH)

    def filter(self, audio: Audio, ban_words: list[str], sound_name: str):
        if not audio.converted_segment_path:
            raise ValueError("File path is None")
        timestamps: list[dict] = self._get_filtered_timestamps(
            file_path=audio.converted_segment_path, ban_words=ban_words)

        log.debug(timestamps)

        if not timestamps:
            return audio.file_path

        new_audio_segment = audio.segment[: timestamps[0]["start"]]

        for i, word in enumerate(timestamps):
            sound_duration = word["end"] - word["start"]
            if sound_name == "Тишина":
                new_audio_segment += AudioSegment.silent(duration=sound_duration)
            elif sound_name == "Дельфин":
                pass
            elif sound_name == "Кря":
                pass
            elif sound_name == "Пик":
                pass

            if i == len(timestamps) - 1:
                new_audio_segment += audio.segment[timestamps[-1]["end"]:]
                completed_audio_path = self._save_segment(
                    audio_segment=new_audio_segment, suffix=audio.extension)
                break

            new_audio_segment += audio.segment[word["end"]:timestamps[i + 1]["start"]]
        return completed_audio_path

    def _get_filtered_timestamps(self, file_path: str, ban_words: list[str]) -> list[dict]:
        timestamps = self._get_timestamps(file_path)
        filtered_timestamps = []

        for word_info in timestamps:
            if word_info["word"] in ban_words:
                filtered_timestamps.append(
                    {
                        "word": word_info["word"],
                        "start": word_info["start"] * 1000,
                        "end": word_info["end"] * 1000,
                    }
                )

        return filtered_timestamps

    def _get_timestamps(self, file_path: str) -> list[dict]:
        with wave.open(file_path, "rb") as wave_file:
            recognizer = KaldiRecognizer(
                self.model, config.REQUIRED_FRAME_RATE)
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
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as completed_audio:
            completed_audio_path = completed_audio.name
            audio_segment.export(completed_audio_path, format=suffix[1:])
        log.debug(completed_audio_path)
        return completed_audio_path
