from nltk.corpus import wordnet as wn
from spacy import symbols as sp

parts_of_speech = {
    sp.VERB: {wn.VERB},
    sp.ADJ: {wn.ADJ, wn.ADJ_SAT},
    sp.NOUN: {wn.NOUN},
    sp.ADV: {wn.ADV}
}