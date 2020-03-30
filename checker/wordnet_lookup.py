from nltk.corpus import wordnet as wn
from common import *
from checker import *
from spacy import symbols as sp

wordnet_by_language = {
    English: 'eng',
    Japanese: 'jpn'
}


def onehop_lemmas_with_synset(language, target_language, word):
    language = wordnet_by_language[language]
    target_language = wordnet_by_language[target_language]
    # what the word can mean in base langauge
    base_synsets = wn.synsets(word, lang=language)

    # how that meaning can be expressed in target language
    hop_lemmas = {lemma for synset in base_synsets for lemma in synset.lemmas(lang=target_language)}

    # what those expressions can mean in target language
    hop_synsets = {synset for lemma in hop_lemmas for synset in wn.synsets(lemma.name(), lang=target_language)}

    # how they can be expressed in base language
    onehop_results= [(lemma, synset) for synset in hop_synsets for lemma in synset.lemmas(lang=language)]

    onehop_lemmas = {x[0]: [] for x in onehop_results}
    for lemma, synset in onehop_results:
        onehop_lemmas[lemma].append(synset)

    return onehop_lemmas

def onehop_lemmas(language, target_language, word):
    return list(onehop_lemmas_with_synset(language, target_language, word).keys())



