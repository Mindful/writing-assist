from lang8_data import load, parse
import unittest

class TestEnglishNlp(unittest.TestCase):
    nlp = parse.english_nlp()

    def test_correction_handling(self):
        doc = TestEnglishNlp.nlp("So, as the winter is coming, I'm [f-blue]starting[/f-blue] to feel [f-red]better[/f-red].")



def main():
    x = load.load_data('head.dat')
    print('wiggity')

if __name__ == '__main__':
    main()