from lang8 import load, parse
import unittest


class MockSpacySpan:
    def __init__(self, text):
        self.text = text


def mock_meta_span(text, type, content=None):
    return parse.MetaSpan(MockSpacySpan(text), type, content)


class TestEnglishNlp(unittest.TestCase):
    nlp = parse.english_nlp()

    def test_lang8_span_parsing(self):
        str1 = "So, as the winter is coming, I'm [f-blue] really starting [/f-blue] to feel [f-red]better [/f-red]."
        str2 = "I like big dogs."
        str3 = "Will you buy me a [sline]small[/sline] dog?"
        str4 = "'I w[f-blue]ould[/f-blue] appreciate it if you [f-blue]could [/f-blue]correct my sentences.'"
        doc1 = TestEnglishNlp.nlp(str1)
        doc2 = TestEnglishNlp.nlp(str2)
        doc3 = TestEnglishNlp.nlp(str3)
        doc4 = TestEnglishNlp.nlp(str4)

        self.assertEqual(doc1.text, parse.operations_regex.sub('', str1))
        self.assertEqual(doc2.text, parse.operations_regex.sub('', str2))
        self.assertEqual(doc3.text, parse.operations_regex.sub('', str3))
        self.assertEqual(doc4.text, parse.operations_regex.sub('', str4))

        self.assertEqual(doc1._.meta_spans, [mock_meta_span('really starting', '[f-blue]'), mock_meta_span('better', '[f-red]')])
        self.assertEqual(doc2._.meta_spans, [])
        self.assertEqual(doc3._.meta_spans, [mock_meta_span('small', '[sline]')])
        self.assertEqual(doc4._.meta_spans, [mock_meta_span('would', '[f-blue]'), mock_meta_span('could', '[f-blue]')])



def main():
    # data = load.load_data('data/chunkfo')
    # learning_english = (ex for ex in data if 'English' in ex.learning_languages)
    # final_data = [ex for ex in learning_english if ex.process()]
    # print('woog')
   unittest.main()



if __name__ == '__main__':
    main()