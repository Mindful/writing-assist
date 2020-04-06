from checker.word_selection import *


def main():
    bwm = BertWordModel('distilbert-base-uncased')
    bwm.suggestions('The comedy was so interesting!', English, Japanese)
    bwm.print_sentence_analysis('The comedy was so interesting!', English, Japanese)









if __name__ == '__main__':
    main()