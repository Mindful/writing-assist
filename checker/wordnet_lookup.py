from nltk.corpus import wordnet as wn
from languages import *

wordnet_by_language = {
    English: 'eng',
    Japanese: 'jpn'
}

def onehop_words_with_synset(language, target_language, word):
    language = wordnet_by_language[language]
    target_language = wordnet_by_language[target_language]
    base_synsets = wn.synsets(word, lang=language)

    hop_lemmas = {lemma for synset in base_synsets for lemma in synset.lemmas(lang=target_language)}

    hop_synsets = {synset for lemma in hop_lemmas for synset in wn.synsets(lemma.name(), lang=target_language)}

    onehop_results= [(lemma, synset) for synset in hop_synsets for lemma in synset.lemmas(lang=language)]

    onehop_lemmas = {x[0]: [] for x in onehop_results}
    for lemma, synset in onehop_results:
        onehop_lemmas[lemma].append(synset)

    return onehop_lemmas

def onehop_words(language, target_language, word):
    return list(onehop_words_with_synset(language, target_language, word).keys())



