import spacy
import re
from spacy.symbols import *
from spacy.matcher import Matcher
from spacy.tokens import Doc


operation_markers = {
    '[f-red]': '[/f-red]',
    '[f-blue]': '[/f-blue]',
    '[sline]': '[/sline]',
}

operations_list = list(operation_markers.keys()) + list(operation_markers.values())

operations_regex = re.compile(r'\s*(' + '|'.join(re.escape(key) for key in operations_list) + r')\s*')

Doc.set_extension("corrections", default=[])


class CorrectionSpanProcessor(object):
    name = "lang8_span_processor"

    def __init__(self, nlp):
        self.nlp = nlp
        patterns = [
            [{ORTH: start_marker}, {"OP": "*"}, {ORTH: end_marker}] for start_marker, end_marker in
            operation_markers.items()
        ]

        matcher = Matcher(nlp.vocab)
        matcher.add('correction', patterns)

        self.matcher = matcher

    def __call__(self, doc):
        matches = self.matcher(doc)
        offset = 0
        span_data = []
        for match_id, start, end in matches:
            span_data.append((doc[start].text, start - offset, end - (offset+2)))
            offset += 2

        words = [token.text for token in doc if token.text not in operations_list]
        spaces = [token.whitespace_ for token in doc if token.text not in operations_list]
        final_doc = Doc(self.nlp.vocab, words, spaces)
        final_doc._.corrections = [(final_doc[x[1]:x[2]], x[0]) for x in span_data]

        return final_doc


#TODO: double check this works iwth more than one correction tag
def english_nlp():
    def pad_span_whitespace(text):
        match_iter = operations_regex.finditer(text)

        string_pieces = []

        last_index = 0
        for match in match_iter:
            match_span = match.span()
            previous_text = text[last_index:match_span[0]]
            last_index = match_span[1]
            string_pieces.extend([previous_text, " ", match.group(0).strip(), " "])

        string_pieces.append(text[last_index:len(text)])

        return "".join(string_pieces).strip()

    nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner"])
    for marker in operations_list:
        nlp.tokenizer.add_special_case(marker, [{ORTH: marker}])

    base_tokenizer = nlp.tokenizer
    nlp.tokenizer = lambda text: base_tokenizer(pad_span_whitespace(text))
    nlp.add_pipe(CorrectionSpanProcessor(nlp), first=True)

    return nlp
