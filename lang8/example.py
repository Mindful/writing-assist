import json
from lang8.parse import  english_nlp, CorrectionSpan
from langdetect import detect_langs
from difflib import SequenceMatcher
from math import log2

parsers = {
    'English': english_nlp()
}

languages = {
    'en': 'English',
    'ja': 'Japanese'
}

class Example:
    # https://sites.google.com/site/naistlang8corpora/home/readme-raw
    __slots__ = ['journal_id', 'learning_languages', 'native_language', 'sentences', 'corrections']

    def __init__(self, raw_data):
        json_data = json.loads(raw_data, strict=False)
        self.journal_id = json_data[0]
        self.learning_languages = [x.strip() for x in json_data[2].split(',')]
        self.native_language = json_data[3]
        self.sentences = json_data[4]
        self.corrections = [x for x in json_data[5] if x]  # discard empty corrections

    def __str__(self):
        return "<{} {}: {} -> {}>".format(self.__class__.__name__,
                                               self.journal_id, self.native_language,
                                               self.learning_languages)

    def __repr__(self):
        return self.__str__()



    def process(self, sim_thresh = -0.2, sim_step = 0.2, sim_max = 0.85):
        if len(self.learning_languages) > 1:
            sentence_text = "\n".join(self.sentences)
            language_probabilities = detect_langs(sentence_text)
            iso = max(language_probabilities, key=lambda x: x.prob).lang
            if iso not in languages:
                return False
            language = languages[iso]
        else:
            language = self.learning_languages[0]

        if language not in parsers:
            return False

        parse = parsers[language]

        self.sentences = [
            parse(sent) for sent in self.sentences
        ]

        self.corrections = [
            Correction([parse(sent) for sent in cor], self.sentences) for cor in self.corrections
        ]

        for corr in self.corrections:
            for aligned_corr in corr.aligned_corrections:
                base_doc = self.sentences[aligned_corr[0]]
                correction_similarity_threshold = min(sim_thresh + log2(len(base_doc)) * sim_step, sim_max)
                if aligned_corr[3] < correction_similarity_threshold:
                    continue

                updates = []
                for op in aligned_corr[1]:
                    if op[0] == 'replace' or op[0] == 'insert':
                        updates.append(CorrectionSpan(base_doc[op[1]:op[2]], op[0], aligned_corr[2][op[3]:op[4]]))
                    elif op[0] == 'delete':
                        updates.append(CorrectionSpan(base_doc[op[1]:op[2]], op[0]))


                base_doc._.corrections = base_doc._.corrections + updates

        return True


class Correction:
    __slots__ = ['aligned_corrections']

    def __init__(self, correction_sentences, base_sentences):
        self.aligned_corrections = []
        for corr in correction_sentences:
            alignment_gen = ((index, SequenceMatcher(None, [t.lower_ for t in base], [t.lower_ for t in corr]))
                             for index, base in enumerate(base_sentences)
                             if index not in (x[0] for x in self.aligned_corrections))
            alignments = [(x[0], x[1], x[1].ratio()) for x in alignment_gen]
            best_alignment = max(alignments, key=lambda x: x[2])
            self.aligned_corrections.append((best_alignment[0], best_alignment[1].get_opcodes(), corr, best_alignment[2]))

    def __str__(self):
        return '<{} for sentences {}>'.format(self.__class__.__name__, ','.join(str(x[0]) for x in self.aligned_corrections))


    def __repr__(self):
        return self.__str__()





