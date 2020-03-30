from lang8.example import Example

# lang8_languages = [('Korean', 'English', 'Japanese', 'Mandarin', 'Traditional Chinese',
#             'Vietnamese', 'German', 'French', 'Other language', 'Spanish',
#             'Indonesian', 'Russian', 'Arabic', 'Thai', 'Swedish', 'Dutch',
#             'Hebrew', 'Tagalog', 'Portuguese(Brazil)', 'Cantonese', 'Italian',
#             'Esperanto', 'Hawaiian', 'Afrikaans', 'Mongolian', 'Hindi', 'Polish',
#             'Finnish', 'Greek', 'Bihari', 'Farsi', 'Urdu', 'Turkish', 'Portuguese(Portugal)',
#             'Bulgarian', 'Norwegian', 'Romanian', 'Albanian', 'Ukrainian', 'Catalan',
#             'Latvian', 'Danish', 'Serbian', 'Slovak', 'Georgian', 'Hungarian', 'Malaysian',
#             'Icelandic', 'Latin', 'Laotian', 'Croatian', 'Lithuanian', 'Bengali', 'Tongan',
#             'Slovenian', 'Swahili', 'Irish', 'Czech', 'Estonian', 'Khmer', 'Javanese', 'Sinhalese',
#             'Sanskrit', 'Armenian', 'Tamil', 'Basque', 'Welsh', 'Bosnian', 'Macedonian', 'Telugu',
#                                  'Uzbek', 'Gaelic', 'Azerbaijanian', 'Tibetan', 'Panjabi', 'Marathi', 'Yiddish', 'Ainu',
#                                  'Haitian', 'Slavic')]


def load_data(filename):
    with open(filename, 'r', encoding='utf8') as lang8_file:
        lines = lang8_file.readlines()

    return [
        Example(line) for line in lines
    ]













