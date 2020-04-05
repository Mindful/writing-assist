from checker.wordnet_lookup import *
from checker.word_selection import *


def main():
    bwm = BertWordModel('distilbert-base-uncased')
    onehop_lemmas(English, Japanese, 'cat')
    doc, target_indices, probabilities = bwm.sentence_word_probs('The comedy was so interesting!')

    token = doc[1]
    candidates = onehop_lemmas(English, Japanese, token.text)

    bwm.print_sentence_analysis('The comedy was so interesting!')







if __name__ == '__main__':
    main()