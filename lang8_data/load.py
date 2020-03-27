import json

id_to_language = dict(enumerate(('Korean', 'English', 'Japanese', 'Mandarin', 'Traditional Chinese',
            'Vietnamese', 'German', 'French', 'Other language', 'Spanish',
            'Indonesian', 'Russian', 'Arabic', 'Thai', 'Swedish', 'Dutch',
            'Hebrew', 'Tagalog', 'Portuguese(Brazil)', 'Cantonese', 'Italian',
            'Esperanto', 'Hawaiian', 'Afrikaans', 'Mongolian', 'Hindi', 'Polish',
            'Finnish', 'Greek', 'Bihari', 'Farsi', 'Urdu', 'Turkish', 'Portuguese(Portugal)',
            'Bulgarian', 'Norwegian', 'Romanian', 'Albanian', 'Ukrainian', 'Catalan',
            'Latvian', 'Danish', 'Serbian', 'Slovak', 'Georgian', 'Hungarian', 'Malaysian',
            'Icelandic', 'Latin', 'Laotian', 'Croatian', 'Lithuanian', 'Bengali', 'Tongan',
            'Slovenian', 'Swahili', 'Irish', 'Czech', 'Estonian', 'Khmer', 'Javanese', 'Sinhalese',
            'Sanskrit', 'Armenian', 'Tamil', 'Basque', 'Welsh', 'Bosnian', 'Macedonian', 'Telugu',
                                 'Uzbek', 'Gaelic', 'Azerbaijanian', 'Tibetan', 'Panjabi', 'Marathi', 'Yiddish', 'Ainu',
                                 'Haitian', 'Slavic')))

language_to_id = {language:id for id, language in id_to_language.items()}


class Example:
    # https://sites.google.com/site/naistlang8corpora/home/readme-raw
    __slots__ = ['journal_id', 'learning_language', 'native_language', 'sentences', 'corrections']

    def __init__(self, raw_data):
        json_data = json.loads(raw_data, strict=False)
        self.journal_id = json_data[0]
        self.learning_language = json_data[2]
        self.native_language = json_data[3]
        self.sentences = json_data[4]
        self.corrections = [x for x in json_data[5] if x] # discard empty corrections

    def __str__(self):
        return "(Lang8{} {}: {} -> {})".format(self.__class__.__name__,
                                               self.journal_id, self.native_language,
                                               self.learning_language)

    def __repr__(self):
        return self.__str__()


def load_data(filename):
    with open(filename, 'r', encoding='utf8') as lang8_file:
        lines = lang8_file.readlines()

    return [
        Example(line) for line in lines
    ]













