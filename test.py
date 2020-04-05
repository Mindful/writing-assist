from lang8 import load, parse, example



def main():
    data = load.load_data('data/chunkfo')
    learning_english = [ex for ex in data if 'English' in ex.learning_languages]

    onlp = parse.english_nlp(True)

    opinionated_correction_groups = [
        [onlp(cor_sent) for cor_sent in x] for x in learning_english[0].correction_groups
    ]


    print('wiggity')


    #final_data = [ex for ex in learning_english if ex.process()]



if __name__ == '__main__':
    main()