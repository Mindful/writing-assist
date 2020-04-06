from transformers import AutoModelWithLMHead
from torch import nn
import torch
import pprint
import spacy
from spacy_transformers import TransformersLanguage, TransformersWordPiecer
from scipy import stats
import numpy as np
from checker.wordnet_lookup import *
from checker.morphology import *


class Suggestion:
    def __init__(self, token, considerations, candidates, suggeston_words):
        self.original_word = token.text
        self.considerations = considerations
        self.candidates = candidates
        self.suggestion_words = suggeston_words

    def orignal_prob(self):
        return self.considerations[self.original_word]

    def __repr__(self):
        dict_repr = {
            'original_word': self.original_word,
            'original_prob': self.orignal_prob(),
            'suggestion_words': self.suggestion_words
        }
        return '<' + self.__class__.__name__ + dict_repr.__repr__() + '>'


class BertWordModel:
    def set_english_parser(self, bert_model):
        nlp = TransformersLanguage(trf_name=bert_model, meta={"lang": "en"})
        nlp.add_pipe(nlp.create_pipe('sentencizer'))
        wp = TransformersWordPiecer.from_pretrained(nlp.vocab, bert_model)
        nlp.add_pipe(wp)
        tagger_nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        nlp.add_pipe(tagger_nlp.tagger)
        self.parser = nlp
        self.vocab = wp.model.vocab
        self.mask_token_id = self.vocab[wp.model._mask_token]
        self.ids_to_tokens = wp.model.ids_to_tokens


    def word_probs(self, words, probs):
        return sorted(((word, probs[self.vocab[word]].item()) for word in words if word in self.vocab),
                      key=lambda x: x[1], reverse=True)


    def __init__(self, bert_model):
        self.bert_lm = AutoModelWithLMHead.from_pretrained(bert_model)
        self.set_english_parser(bert_model)
        self.softmax = nn.Softmax(dim=0)
        self.printer = pp = pprint.PrettyPrinter()

    def sentence_word_probs(self, sentence):
        doc = self.parser(sentence)
        token_targets = [tok_index for tok_index, token in enumerate(doc) if token.pos in parts_of_speech]
        targets = [(tok_index, wp_index) for tok_index in token_targets for wp_index in doc._.trf_alignment[tok_index]]
        wordpiece_targets = [x[1] for x in targets]

        input_id_matrix = [doc._.trf_word_pieces.copy() for _ in wordpiece_targets]
        for i in range(len(wordpiece_targets)):
            input_id_matrix[i][wordpiece_targets[i]] = self.mask_token_id

        #TODO: this would ideally be batch_encode_plus once spacy-transformers is compatible with latest transformers
        bert_input = {
            'input_ids': torch.tensor(input_id_matrix)
        }

        with torch.no_grad():
            bert_output = self.bert_lm(**bert_input)[0]

        target_rows = torch.zeros(len(wordpiece_targets), self.bert_lm.config.vocab_size)
        for index, target_index in enumerate(wordpiece_targets):
            target_rows[index] = bert_output[index, target_index]

        return doc, targets, target_rows


    def suggestions(self, sentence, base_language, target_language):
        doc, targets, weights = self.sentence_word_probs(sentence)
        suggestions = []

        for index, target_tuple in enumerate(targets):
            tok_target, wp_target = target_tuple
            wp_token = doc._.trf_word_pieces_[wp_target]
            original_token = doc[tok_target]
            consideration_count = int(0.01 * self.bert_lm.config.vocab_size)

            weight_sort_indices = torch.argsort(weights[index], descending=True)
            considerations = weight_sort_indices[0:consideration_count]
            with torch.no_grad():
                softmaxed_candidates = self.softmax(torch.take(weights[index], considerations))

            consideration_probs = {
                self.ids_to_tokens[considerations[index].item()]: softmaxed_candidates[index].item()
                for index in range(considerations.shape[0])
            }

            # if original token isn't in BERT's top 1%, probably not going to get useful results
            if original_token.text in consideration_probs:
                original_prob = consideration_probs[original_token.text]
                twohop_lemmas = token_candidates(base_language, target_language, original_token)
                if original_token.pos == VERB:
                    # if it's a verb, make sure we keep the tense
                    tense = best_verb_tense(original_token.text)
                    if tense is None:
                        print('warning: skipping becuase verb tense is none for', original_token.text) #TODO: logging?
                        continue
                    twohop_lemmas = (verb_to_tense(lemma, tense) for lemma in twohop_lemmas)

                candidates = {
                    lemma: consideration_probs[lemma] for lemma in twohop_lemmas
                    if lemma in consideration_probs and consideration_probs[lemma] / original_prob > 0.1 # MAGIC NUMBER ALERT
                    # candidates are at least one order of magnitude more likely
                }

                skew = stats.skew(np.array(list(consideration_probs.values())))
                if skew > 1: # MAGIC NUMBER ALERT
                    best_candidate = max(candidates.items(), key=lambda x: x[1])
                    suggestion_words = dict(candidate_tuple for candidate_tuple in candidates.items()
                                  if candidate_tuple[1] >= best_candidate[1] * 0.8)

                    suggestions.append(Suggestion(original_token, consideration_probs, candidates, suggestion_words))

        return suggestions



    def print_sentence_analysis(self, sentence, base_language, target_langage):
        doc, targets, weights = self.sentence_word_probs(sentence)
        probs = torch.nn.Softmax(dim=1)(weights)
        analysis = []

        for index, target_tuple in enumerate(targets):
            tok_target, wp_target = target_tuple
            wp_token = doc._.trf_word_pieces_[wp_target]
            original_token = doc[tok_target]


            tokens_by_likelyhood = torch.argsort(probs[index], descending=True)
            top = tokens_by_likelyhood[0:20]
            top_probs = torch.take(probs[index], top)

            top_tokens = [self.ids_to_tokens[id.item()] for id in top]
            token_analysis = {
                'original_token': original_token,
                'wordpiece_token': wp_token,
                'token_prob': probs[index][self.vocab[wp_token]].item(),
                'top_probs': [(top_tokens[i], top_probs[i].item()) for i in range(len(top_tokens))],
                'twohop_probs': self.word_probs(token_candidates(English, Japanese, original_token), probs[index])


            }
            analysis.append(token_analysis)

        self.printer.pprint(analysis)

    def batch_word_probs(self, text):
        pass





