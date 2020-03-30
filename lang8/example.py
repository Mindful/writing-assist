import json
from lang8.parse import  english_nlp, MetaSpan
from langdetect import detect_langs
from difflib import SequenceMatcher
from math import log2
from common import *

parsers = {
    English: english_nlp()
}

language_by_iso = {
    'en': English,
    'ja': Japanese
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
        return str({attr: getattr(self, attr) for attr in self.__slots__})

    def __repr__(self):
        return "<{} {}: {} -> {}>".format(self.__class__.__name__,
                                               self.journal_id, self.native_language,
                                               self.learning_languages)

    def process(self):
        if len(self.learning_languages) > 1:
            sentence_text = "\n".join(self.sentences)
            language_probabilities = detect_langs(sentence_text)
            iso = max(language_probabilities, key=lambda x: x.prob).lang
            if iso not in language_by_iso:
                return False
            language = language_by_iso[iso]
        else:
            language = self.learning_languages[0]

        if language not in parsers:
            return False

        parse = parsers[language]

        self.sentences = [
            parse(sent) for sent in self.sentences
        ]

        self.corrections = [
            CorrectionGroup([parse(sent) for sent in cor], self.sentences) for cor in self.corrections
        ]

        self._write_corrections_to_meta_spans(self.corrections, self.sentences)

        return True

    @staticmethod
    def _write_corrections_to_meta_spans(corrections, sentences, sim_thresh=-0.2, sim_step=0.2, sim_max=0.85):
        for corr in corrections:
            for aligned_corr in corr.corrections:
                base_doc = sentences[aligned_corr.alignment]
                correction_similarity_threshold = Example._compute_similarity_threshold(base_doc, sim_thresh,
                                                                                        sim_step, sim_max)
                if aligned_corr.similarity_ratio < correction_similarity_threshold:
                    continue

                updates = []
                for op in aligned_corr.comparison_ops:
                    if op[0] == 'replace' or op[0] == 'insert':
                        updates.append(MetaSpan(base_doc[op[1]:op[2]], op[0], aligned_corr.correction[op[3]:op[4]]))
                    elif op[0] == 'delete':
                        updates.append(MetaSpan(base_doc[op[1]:op[2]], op[0]))

                base_doc._.meta_spans = base_doc._.meta_spans + updates

    @staticmethod
    def _compute_similarity_threshold(base_doc, sim_thresh, sim_step, sim_max):
        return min(sim_thresh + log2(len(base_doc)) * sim_step, sim_max)


class CorrectionGroup:
    __slots__ = ['corrections']

    def __init__(self, correction_sentences, base_sentences):
        self.corrections = []
        for corr in correction_sentences:
            alignment_gen = ((index, SequenceMatcher(None, [t.lower_ for t in base], [t.lower_ for t in corr]))
                             for index, base in enumerate(base_sentences)
                             if index not in (x.alignment for x in self.corrections))
            alignments = [(x[0], x[1], x[1].ratio()) for x in alignment_gen]
            best_alignment = max(alignments, key=lambda x: x[2])

            self.corrections.append(Correction(best_alignment[0], corr, best_alignment[2], best_alignment[1].get_opcodes()))

    def __str__(self):
        return str(self.corrections)

    def __getitem__(self, item):
        return self.corrections[item]

    def __repr__(self):
        return '<{} for sentences {}, {} corrections>'.format(self.__class__.__name__,
                                                              '&'.join(str(x.alignment) for x in self.corrections),
                                                              len(self.corrections))

    def __len__(self):
        return len(self.corrections)


class Correction(SlotPrinter):
    __slots__ = ['alignment', 'correction', 'similarity_ratio', 'comparison_ops']

    def __init__(self, alignment, correction, similarity_ratio, comparison_ops):
        self.alignment = alignment
        self.correction = correction
        self.similarity_ratio = similarity_ratio
        self.comparison_ops = comparison_ops







