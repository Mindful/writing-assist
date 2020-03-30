from lang8 import load, parse, example



def main():
    data = load.load_data('data/chunkfo')
    learning_english = (ex for ex in data if 'English' in ex.learning_languages)
    final_data = [ex for ex in learning_english if ex.process()]



if __name__ == '__main__':
    main()