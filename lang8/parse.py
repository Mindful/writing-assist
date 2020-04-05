import spacy
import re
import itertools
from spacy.tokens import Doc
from common import SlotPrinter


deletion_markers = ['[f-red]', '[sline]']
retention_markers = ['[f-blue]']
markers = deletion_markers + retention_markers
operation_markers = {m: m[0:1] + '/' + m[1:] for m in markers}


class MetaSpan(SlotPrinter):
    __slots__ = ['start', 'end', 'type', 'content']

    def __init__(self, start, end, type, content=None):
        self.start = start
        self.end = end
        self.type = type
        self.content = content

    def __eq__(self, other):
        return isinstance(other, MetaSpan) and self.type == other.type and self.start == other.start \
               and self.end == other.end and self.content == other.content


operations_list = list(operation_markers.keys()) + list(operation_markers.values())
operations_regex = re.compile('(' + '|'.join(re.escape(op) for op in operations_list) + ')')
Doc.set_extension("meta_spans", default=[])


class CorrectionTokenizer:

    def __init__(self, tokenizer, enact_corrections):
        self.tokenizer = tokenizer
        self.enact_corrections = enact_corrections


    def extract_corrections(self, text):
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
            correction_type = start_match.group(0)

            previous_text = text[last_index:start_span[0]]
            inner_text = text[start_span[1]:end_span[0]]

            left_padding = sum(1 for _ in itertools.takewhile(str.isspace,inner_text))
            right_padding = sum(1 for _ in itertools.takewhile(str.isspace,reversed(inner_text)))

            offset_update = len(start_match.group(0)) + len(end_match.group(0))

            correction_start = start_span[0] + left_padding - offset
            correction_end = end_span[1] - right_padding - offset - offset_update
            offset += offset_update

            if self.enact_corrections and correction_type in deletion_markers:
                # remove text marked for deletion from the correction
                offset += len(inner_text)
                string_pieces.append(previous_text)
                correction_end = correction_start
                content = inner_text.as_doc()
            else:
                content = None
                string_pieces.extend([previous_text, inner_text])


            last_index = end_span[1]
            corrections.append((correction_type, correction_start, correction_end, content))

        string_pieces.append(text[last_index:len(text)])

        return "".join(string_pieces).strip(), corrections




    def __call__(self, text):
        clean_text, corrections = self.extract_corrections(text)
        doc = self.tokenizer(clean_text)
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

            charspan = doc.char_span(start, end)
            if cor[1] == cor[2]:  # it's a deletion marker, we only need a deletion location
                doc_corrections.append(MetaSpan(charspan.start, charspan.start, cor[0], cor[3]))
            else:
                doc_corrections.append(MetaSpan(charspan.start, charspan.end, cor[0], cor[3]))

        doc._.meta_spans = doc_corrections
        return doc



def english_nlp(enact=False):
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    nlp.tokenizer = CorrectionTokenizer(nlp.tokenizer, enact)
    return nlp
