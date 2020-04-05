from checker.wordnet_lookup import *
from checker.word_selection import *


def main():
    s = 'The comedy was so interesting!'
    bwm = BertWordModel('distilbert-base-uncased')
    doc, target_indices, probabilities = bwm.sentence_word_probs(s)

    bwm.print_sentence_analysis(s)









if __name__ == '__main__':
    main()