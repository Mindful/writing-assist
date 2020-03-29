from transformers import DistilBertForMaskedLM, DistilBertTokenizer
from transformers import AutoModelWithLMHead, AutoTokenizer
from torch import nn
import torch
import string
import pprint


class BertWordModel:
    def __init__(self, bert_model):
        self.bert_lm = AutoModelWithLMHead.from_pretrained(bert_model)
        self.bert_tokenizer = AutoTokenizer.from_pretrained(bert_model)
        self.softmax = nn.Softmax(dim=1)
        self.printer = pp = pprint.PrettyPrinter()

    def sentence_word_probs(self, sentence):
        tokens = self.bert_tokenizer.tokenize(sentence)
        target_indices = [index for index, token in enumerate(tokens) if token not in string.punctuation]
        token_matrix = [tokens.copy() for _ in target_indices]
        for i in range(len(target_indices)):
            token_matrix[i][i] = self.bert_tokenizer.mask_token

        bert_input = self.bert_tokenizer.batch_encode_plus(token_matrix, add_special_tokens=True, return_tensors='pt')
        with torch.no_grad():
            bert_output = self.bert_lm(**bert_input)[0]

        target_rows = torch.zeros(len(target_indices), self.bert_lm.config.vocab_size)
        for index, target_index in enumerate(target_indices):
            target_rows[index] = bert_output[index, target_index+1]  # +1 for CLS token

        return tokens, target_indices, self.softmax(target_rows)

    def print_sentence_analysis(self, sentence):
        tokens, targets, probs = self.sentence_word_probs(sentence)
        vocab = self.bert_tokenizer.get_vocab()
        analysis = []

        for target in targets:
            original_token = tokens[target]
            tokens_by_likelyhood = torch.argsort(probs[target], descending=True)
            top = tokens_by_likelyhood[0:20]
            top_probs = torch.take(probs[target], top)
            top_tokens = self.bert_tokenizer.convert_ids_to_tokens(top)
            analysis.append(((original_token, probs[target][vocab[original_token]]),
                             [(top_probs[i].item(), top_tokens[i]) for i in range(len(top_tokens))]))

        self.printer.pprint(analysis)

    def batch_word_probs(self, text):
        pass


def main():
    bwm = BertWordModel('distilbert-base-uncased')
    bwm.print_sentence_analysis('I love dogs so much.')




