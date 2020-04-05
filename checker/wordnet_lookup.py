from nltk.corpus import wordnet as wn
from common import *
from checker import *
from spacy import symbols as sp

wordnet_by_language = {
    English: 'eng',
    Japanese: 'jpn'
}


def twohop_lemmas_with_synset(language, target_language, word):
    language = wordnet_by_language[language]
    target_language = wordnet_by_language[target_language]
    # what the word can mean in base langauge
    base_synsets = wn.synsets(word, lang=language)

    # how that meaning can be expressed in target language
    hop_lemmas = {lemma for synset in base_synsets for lemma in synset.lemmas(lang=target_language)}

    # what those expressions can mean in target language
    hop_synsets = {synset for lemma in hop_lemmas for synset in wn.synsets(lemma.name(), lang=target_language)}

    # how they can be expressed in base language
    onehop_results = [(lemma, synset) for synset in hop_synsets for lemma in synset.lemmas(lang=language)]

    onehop_lemmas = {x[0]: [] for x in onehop_results}
    for lemma, synset in onehop_results:
        onehop_lemmas[lemma].append(synset)

    return onehop_lemmas


def token_candidates(language, target_language, token):
    target_pos = parts_of_speech[token.pos]
    twohop_lemma_map = twohop_lemmas_with_synset(language, target_language, token.text)
    candidate_names = [lemma.name() for lemma, synset_list in twohop_lemma_map.items()
                       if synset_list[0].pos() in target_pos]
    return candidate_names



