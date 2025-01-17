import json
from pydub import AudioSegment
from re import findall
import tempfile
from vosk import KaldiRecognizer, Model, SetLogLevel
import wave

from config import MODEL_PATH, REQUIRED_FRAME_RATE, FRAME_BLOCK_SIZE
from logger import ColorLogger
from media import Audio

SetLogLevel(0)
log = ColorLogger(name="Media").get_logger()


class Processor:
    """Обработчик аудиофайлов"""

    def __init__(self):
        self.model = Model(MODEL_PATH)
        self.__load_regex()

    def filter(self, audio: Audio, ban_words: list[str], sound_name: str) -> str:
        timestamps: list[dict] = self._get_filtered_timestamps(
            file_path=audio.converted_audio_path, ban_words=ban_words)

        if not timestamps:
            completed_audio_path = self._save_segment(audio_segment=audio.segment, suffix=audio.extension)
            return completed_audio_path

        filtered_audio_segment = audio.segment[:timestamps[0]["start"]]

        for i, word in enumerate(timestamps):
            sound_duration = word["end"] - word["start"]

            filtered_audio_segment += self._add_sound(
                duration=sound_duration, name=sound_name
            )

            if i == len(timestamps) - 1:
                filtered_audio_segment += audio.segment[timestamps[-1]["end"]:]
                completed_audio_path = self._save_segment(
                    audio_segment=filtered_audio_segment, suffix=audio.extension
                )
                break

            filtered_audio_segment += audio.segment[word["end"]: timestamps[i + 1]["start"]]
        return completed_audio_path

    def _get_filtered_timestamps(self, file_path: str, ban_words: list[str] | set[str]) -> list[dict]:
        recognaze_info = self._get_recognaze_info(file_path)
        timestamps = recognaze_info['result']
        filtered_timestamps = []

        if not ban_words:
            ban_words = set(self._detect_profanity(recognaze_info['text']))

        log.info('Awoided words: %s', ban_words)

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

    def _get_recognaze_info(self, file_path: str) -> dict:
        with wave.open(file_path, "rb") as wave_file:
            recognizer = KaldiRecognizer(self.model, REQUIRED_FRAME_RATE)
            recognizer.SetWords(True)
            while True:
                data = wave_file.readframes(FRAME_BLOCK_SIZE)
                if len(data) == 0:
                    break
                recognizer.AcceptWaveform(data)
            recognaze_info = json.loads(recognizer.FinalResult())
        return recognaze_info

    def _detect_profanity(self, text: str) -> list[str]:
        matches = findall(self.regex, text)
        return matches

    def _add_sound(self, duration: int, name: str) -> AudioSegment:
        if name == "Тишина":
            return AudioSegment.silent(duration=duration)
        else:
            sound = AudioSegment.from_wav(f"sounds\{name}.wav")
            return sound[:duration]

    def _save_segment(self, audio_segment: AudioSegment, suffix: str) -> str:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as completed_audio:
            completed_audio_path = completed_audio.name
            audio_segment.export(completed_audio_path, format=suffix[1:])
        return completed_audio_path

    def __load_regex(self):
        with open("profanity_regex.txt", "r", encoding="utf-8") as file:
            regex = file.read().strip()
        self.regex = regex
