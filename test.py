from lang8 import load, parse, example



def main():
    data = load.load_data('data/chunkfo')
    learning_english = [ex for ex in data if 'English' in ex.learning_languages]
    final_data = [ex for ex in learning_english[:5] if ex.process()]
    grammar_checked_correction_ex(final_data)

def grammar_checked_correction_ex(examples):
    initial_correction_count = 0
    grammatical_count = 0

    for ex in examples:
        initial_v_grammatical = [
            (corr_group.corrections, corr_group.grammatical_corrections) 
            for corr_group in ex.correction_groups
            if corr_group.grammar_check_corrections()
        ]

        initial_correction_count += sum(len(initial) for initial, grammatical in initial_v_grammatical)
        grammatical_count += sum(len(grammatical) for initial, grammatical in initial_v_grammatical)

        for initial, grammatical in initial_v_grammatical:
            print("All Corrections:", [corr.doc for corr in initial])
            print("Grammatical:", [corr.doc for corr in grammatical])
            print()

    print("Total initial corrections: {}".format(initial_correction_count))
    print("Number of ungrammatical corrections removed: {}".format(initial_correction_count - grammatical_count))


if __name__ == '__main__':
    main()
