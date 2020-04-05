from transformers import AutoModelWithLMHead
from torch import nn
import torch
import pprint
import spacy
from spacy_transformers import TransformersLanguage, TransformersWordPiecer
from checker import parts_of_speech
from checker.wordnet_lookup import *


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
        self.softmax = nn.Softmax(dim=1)
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

        return doc, targets, self.softmax(target_rows)

    def print_sentence_analysis(self, sentence, base_language, target_langage):
        doc, targets, probs = self.sentence_word_probs(sentence)
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


def main():
    bwm = BertWordModel('distilbert-base-uncased')
    bwm.print_sentence_analysis('I love dogs so much.')




