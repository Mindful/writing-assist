from lang8 import load, parse, example
import unittest
import re


class MockSpacySpan:
    def __init__(self, text):
        self.text = text


def mock_meta_span(text, type, content=None):
    return parse.MetaSpan(MockSpacySpan(text), type, content)


def compute_correction_result(original_doc,  correction):
    tokens = [t.lower_ for t in original_doc]
    for op in correction.comparison_ops:
        op_type = op[0]
        if op_type == 'equal':
            continue

        doc_correction = next(cor_span for cor_span in original_doc._.meta_spans if cor_span.type == op_type
             and cor_span.span.start == op[1] and cor_span.span.end == op[2] and (cor_span.type == 'delete' or
                cor_span.content.lower_ == correction.doc[op[3]:op[4]].lower_))

        if doc_correction.type == 'replace' or doc_correction.type == 'insert':
            tokens[doc_correction.span.start:doc_correction.span.end] = [t.lower_ for t in doc_correction.content]
        elif doc_correction.type == 'delete':
            tokens[doc_correction.span.start:doc_correction.span.end] = []

    return tokens



class Lang8(unittest.TestCase):
    nlp = parse.english_nlp()
    opinionated_nlp = parse.english_nlp(True)

    deletion_span_markers = [re.escape(m) + r'.*' + re.escape(m[0:1] + '/' + m[1:]) for m in parse.deletion_markers]

    retention_op_markers = [re.escape(x) for x in parse.retention_markers] + [re.escape(x) for x in [parse.operation_markers[m] for m in parse.retention_markers]]

    opinionated_deletion_regex = re.compile('(' + '|'.join(op for op in deletion_span_markers + retention_op_markers) + ')')

    def verify_corrections(self, sentences, correction_groups):
        example.Example._write_corrections_to_meta_spans(correction_groups, sentences,
                                                         sim_thresh=-0.2, sim_step=0.2, sim_max=0.85)

        done_corrections = 0
        seen_corrections = 0
        for index, sentence_doc in enumerate(sentences):
            seen_corrections += len(sentence_doc._.meta_spans)
            for group in correction_groups:
                for correction in (x for x in group if x.alignment == index):
                    thresh = example.Example._compute_similarity_threshold(sentence_doc,
                                                                           sim_thresh=-0.2, sim_step=0.2, sim_max=0.85)

                    if correction.similarity_ratio >= thresh:
                        target = [t.lower_ for t in correction.doc]
                        result = compute_correction_result(sentence_doc, correction)
                        self.assertEqual(target, result)
                        done_corrections += 1

        self.assertEqual(seen_corrections, done_corrections)


    def test_enacting_correction_parsing(self):
        str1 = "So, as the winter is coming, I'm [f-blue] really starting [/f-blue] to feel [f-red]better [/f-red]."
        str2 = "I like big dogs."
        str3 = "Will you buy me a [sline]small[/sline] dog?"
        str4 = "'I w[f-blue]ould[/f-blue] appreciate it if you [f-blue]could [/f-blue]correct my sentences.'"
        doc1 = Lang8.opinionated_nlp(str1)
        doc2 = Lang8.opinionated_nlp(str2)
        doc3 = Lang8.opinionated_nlp(str3)
        doc4 = Lang8.opinionated_nlp(str4)


        self.assertEqual(doc1.text, Lang8.opinionated_deletion_regex.sub('', str1))
        self.assertEqual(doc2.text, Lang8.opinionated_deletion_regex.sub('', str2))
        self.assertEqual(doc3.text, Lang8.opinionated_deletion_regex.sub('', str3))
        self.assertEqual(doc4.text, Lang8.opinionated_deletion_regex.sub('', str4))

        self.assertEqual(doc1._.meta_spans, [mock_meta_span('really starting', '[f-blue]'),
                                             mock_meta_span('', '[f-red]', 'better ')])
        self.assertEqual(doc2._.meta_spans, [])
        self.assertEqual(doc3._.meta_spans, [mock_meta_span('', '[sline]', 'small')])
        self.assertEqual(doc4._.meta_spans, [mock_meta_span('would', '[f-blue]'), mock_meta_span('could', '[f-blue]')])


    def test_correction_span_parsing(self):
        str1 = "So, as the winter is coming, I'm [f-blue] really starting [/f-blue] to feel [f-red]better [/f-red]."
        str2 = "I like big dogs."
        str3 = "Will you buy me a [sline]small[/sline] dog?"
        str4 = "'I w[f-blue]ould[/f-blue] appreciate it if you [f-blue]could [/f-blue]correct my sentences.'"
        doc1 = Lang8.nlp(str1)
        doc2 = Lang8.nlp(str2)
        doc3 = Lang8.nlp(str3)
        doc4 = Lang8.nlp(str4)

        self.assertEqual(doc1.text, parse.operations_regex.sub('', str1))
        self.assertEqual(doc2.text, parse.operations_regex.sub('', str2))
        self.assertEqual(doc3.text, parse.operations_regex.sub('', str3))
        self.assertEqual(doc4.text, parse.operations_regex.sub('', str4))

        self.assertEqual(doc1._.meta_spans, [mock_meta_span('really starting', '[f-blue]'), mock_meta_span('better', '[f-red]')])
        self.assertEqual(doc2._.meta_spans, [])
        self.assertEqual(doc3._.meta_spans, [mock_meta_span('small', '[sline]')])
        self.assertEqual(doc4._.meta_spans, [mock_meta_span('would', '[f-blue]'), mock_meta_span('could', '[f-blue]')])


    def test_correction_object_construction(self):
        sentences = [Lang8.nlp(x) for x in [
            "I like big dogs.",
            "Will you buy me a big dog?",
            "I hope that it won't be a small dog."
        ]]

        correction_sentences = [[Lang8.nlp(x) for x in y] for y in [
            [
                "Will you buy me a [sline]small[/sline] dog?"
            ],
            [
                "I like huge dogs.",
                "Will you buy me a huge dog?"
            ],
            [
                "Best deals on [f-red]cheap[/f-red] cars here, buy now!"
            ]
        ]]

        corrections = [example.CorrectionGroup(cs, sentences) for cs in correction_sentences]

        for index, cor in enumerate(corrections):
            self.assertEqual(len(cor), len(correction_sentences[index]))

        self.assertEqual(corrections[0][0].alignment, 1)
        self.assertEqual(corrections[1][0].alignment, 0)
        self.assertEqual(corrections[1][1].alignment, 1)

        self.verify_corrections(sentences, corrections)

    def test_correction_object_construction2(self):
        sentences = [Lang8.nlp(x) for x in ['Autumnal leaves',
             'In Japan, autumnal leaves are getting beautiful.',
             'Japanese autumn is colored by many colors.',
             "I wanted to take photos, but I didn't have enough time to do it.",
             "I'm going to take photos this Sunday, but the leaves might already hurt.",
             "I think I'm going to go to Kyoto.",
             'I hope it will be fine.']
        ]

        correction_sentences = [[Lang8.nlp(x) for x in y] for y in [['[f-blue]Autumn L[/f-blue]eaves'],
             ['In Japan, [f-blue]the autumn[/f-blue] leaves are getting beautiful.'],
             ["Japan[f-blue]'s[/f-blue] autumn[f-blue]s[/f-blue] [f-blue]are filled with[/f-blue] many colors."],
             ['I\'m going to take photos this Sunday, but the leaves might already [f-red]hurt[/f-red]. (I\'m not sure what you mean by "hurt")']]]

        corrections = [example.CorrectionGroup(cs, sentences) for cs in correction_sentences]

        for index, cor in enumerate(corrections):
            self.assertEqual(len(cor), len(correction_sentences[index]))

        self.assertEqual(corrections[0][0].alignment, 0)
        self.assertEqual(corrections[1][0].alignment, 1)
        self.assertEqual(corrections[2][0].alignment, 2)
        self.assertEqual(corrections[3][0].alignment, 4)

        self.verify_corrections(sentences, corrections)



def main():
    unittest.main()


if __name__ == '__main__':
    main()