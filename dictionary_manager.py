import os
import json
from logger import ColorLogger

log = ColorLogger(name="DictionaryManager").get_logger()


def load_words_from_json(path):
    log.info(f"Loading words from {path}")
    with open(path, "r", encoding="utf-8") as f:
        words = json.load(f)
    if not isinstance(words, list):
        log.error("JSON is not a list")
        return []
    log.debug(f"Loaded words: {words}")
    return words


def remove_custom_dictionary(path):
    if os.path.isfile(path) and path != "words.json":
        os.remove(path)
        log.info(f"Removed custom dictionary {path}")
