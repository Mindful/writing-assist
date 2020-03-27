from lang8 import load, parse
import unittest


class TestEnglishNlp(unittest.TestCase):
    nlp = parse.english_nlp()

    def test_correction_handling(self):
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

        self.assertEqual([(x[0].text, x[1]) for x in doc1._.corrections],
                         [('really starting', '[f-blue]'), ('better', '[f-red]')])
        self.assertEqual([(x[0].text, x[1]) for x in doc2._.corrections], [])
        self.assertEqual([(x[0].text, x[1]) for x in doc3._.corrections], [('small', '[sline]')])
        self.assertEqual([(x[0].text, x[1]) for x in doc4._.corrections],
                         [(None, '[f-blue]'), ('could', '[f-blue]')])


        print('woogity')



def main():
    unittest.main()

if __name__ == '__main__':
    main()