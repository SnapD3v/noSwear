class MediaSession:
    def __init__(self, file_path, sound=None, dictionary_choice=None, waiting_for_dict_file=False):
        self.file_path = file_path
        self.sound = sound
        self.dictionary_choice = dictionary_choice
        self.waiting_for_dict_file = waiting_for_dict_file
