from checker.word_selection import *
from checker.morphology import *
from checker.wordnet_lookup import *
import spacy

def main():
    bwm = BertWordModel('distilbert-base-uncased')
    s1 = bwm.suggestions('The comedy was so interesting!', English, Japanese)
    s2 = bwm.suggestions('Today I watched a drama.', English, Japanese)

    bwm.print_sentence_analysis('The comedy was so interesting!', English, Japanese)



def morphology():
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    t = nlp('watched')[0]
    best_verb_tense(t.text) #TODO: first call always returns none WHY?
    best_verb_tense(t.text)
    candidates = token_candidates(English, Japanese, t)
    candidates = [x for x in candidates if best_verb_tense(x)]










if __name__ == '__main__':
    main()
    #morphology()