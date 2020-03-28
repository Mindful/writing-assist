from transformers import DistilBertForMaskedLM, DistilBertTokenizer
from torch import nn
import torch


def main():
    #TODO: try this with biger bert, see if probs change
    #TODO: we need to actually mask words - bert can clearly see the words it's guessing like this
    with torch.no_grad():
        tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        lm = DistilBertForMaskedLM.from_pretrained('distilbert-base-uncased')

        #sent = "I like dogs very much"
        sent = "I squat dogs very much"
        t = tokenizer.encode_plus(sent, add_special_tokens=True, return_tensors='pt')
        r = lm(t['input_ids'], attention_mask=t['attention_mask'])
        probs = r[0][0]
        sm = nn.Softmax(dim=1)
        token_list = tokenizer.convert_ids_to_tokens(t['input_ids'][0])

        final = sm(probs)
        for i in range(1, final.shape[0]):
            original_token = token_list[i]
            tokens_by_likelyhood = torch.argsort(final[i], descending=True)
            top = tokens_by_likelyhood[0:20]
            top_probs = torch.take(final[i], top)
            top_tokens = tokenizer.convert_ids_to_tokens(top)

            print(original_token, top_tokens, top_probs)





