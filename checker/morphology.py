from pattern.en import tenses, conjugate
from collections import Counter


def best_verb_tense(verb):
    try:
        tense_counts = Counter(x[0] for x in tenses(verb))
        if len(tense_counts) == 0:
            return None
        best_tense = max(tense_counts, key=lambda x: tense_counts[x])
        return best_tense
    except RuntimeError as error:
        # we don't know that verb
        return None

#TODO: super hacky but necessary, see https://github.com/clips/pattern/issues/243#issuecomment-428317658
best_verb_tense('stopgap')

def verb_to_tense(verb, tense):
    return conjugate(verb, tense=tense)



