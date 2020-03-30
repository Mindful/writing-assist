import spacy
import re
import itertools
from spacy.tokens import Doc
from common import SlotPrinter


operation_markers = {
    '[f-red]': '[/f-red]',
    '[f-blue]': '[/f-blue]',
    '[sline]': '[/sline]',
}


class MetaSpan(SlotPrinter):
    __slots__ = ['span', 'type', 'content']

    def __init__(self, span, type, content=None):
        self.span = span
        self.type = type
        self.content = content

    def __eq__(self, other):
        return isinstance(other, MetaSpan) and self.type == other.type and self.span.text == other.span.text \
               and self.content == other.content


operations_list = list(operation_markers.keys()) + list(operation_markers.values())
operations_regex = re.compile('(' + '|'.join(re.escape(op) for op in operations_list) + ')')
Doc.set_extension("meta_spans", default=[])


def extract_corrections(text):
    matches = list(operations_regex.finditer(text))

    string_pieces = []
    corrections = []

    last_index = 0
    offset = 0
    for i in range(0, len(matches), 2):
        start_match = matches[i]
        end_match = matches[i+1]

        start_span = start_match.span()
        end_span = end_match.span()

        previous_text = text[last_index:start_span[0]]
        inner_text = text[start_span[1]:end_span[0]]

        left_padding = sum(1 for _ in itertools.takewhile(str.isspace,inner_text))
        right_padding = sum(1 for _ in itertools.takewhile(str.isspace,reversed(inner_text)))

        offset_update = len(start_match.group(0)) + len(end_match.group(0))

        correction_start = start_span[0] + left_padding - offset
        correction_end = end_span[1] - right_padding - offset - offset_update
        offset += offset_update

        last_index = end_span[1]
        corrections.append((start_match.group(0), correction_start, correction_end))
        string_pieces.extend([previous_text, inner_text])

    string_pieces.append(text[last_index:len(text)])

    return "".join(string_pieces).strip(), corrections


def corrections_tokenizer(tokenizer):
    def tokenize(text):
        clean_text, corrections = extract_corrections(text)
        doc = tokenizer(clean_text)
        doc_corrections = []
        for cor in corrections:
            token_starts = [t.idx for t in doc]
            start = -1
            end = -1
            for index, char_location in enumerate(token_starts):
                if char_location <= cor[1]:
                    start = char_location
                if char_location <= cor[2]:
                    end = char_location + len(doc[index])

                if char_location > cor[1] and char_location > cor[2]:
                    break

            doc_corrections.append(MetaSpan(doc.char_span(start, end), cor[0]))

        doc._.meta_spans = doc_corrections
        return doc

    return tokenize


def english_nlp():
    nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner"])
    nlp.tokenizer = corrections_tokenizer(nlp.tokenizer)
    return nlp
