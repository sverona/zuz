import re
from argparse import ArgumentParser


def build_lexicon(wordlist):
    
    with open(wordlist) as words:
        lexicon = {}
        for line in words.readlines():
            word, defn = line.strip().split("\t")
            lexicon[word] = {}
            lexicon[word]['definition'] = defn

        for word in lexicon:
            if word[1:] in lexicon:
                # print("Front hook: %s -> %s" % (word[1:], word))
                front_hooks = lexicon[word[1:]].get('front_hooks', [])
                lexicon[word[1:]]['front_hooks'] = front_hooks + [word[0]]
                lexicon[word]['front_inner_hook'] = True
            if word[:-1] in lexicon:
                """
                if word[-1] != "S":
                    print("Back hook:  %s -> %s" % (word[:-1], word))
                    """
                back_hooks = lexicon[word[:-1]].get('backhooks', [])
                lexicon[word[:-1]]['back_hooks'] = back_hooks + [word[-1]]
                lexicon[word]['back_inner_hook'] = True

            lexicon[word]['length'] = len(word)
            lexicon[word]['vowels'] = len([c for c in word if c in "AEIOU"])
            lexicon[word]['pct_vowels'] = 100 * lexicon[word]['vowels'] // len(word)
            lexicon[word]['consonants'] = len(word) - lexicon[word]['vowels']
            lexicon[word]['pct_consonants'] = 100 - lexicon[word]['pct_vowels']

        for word, fields in lexicon.items():
            if 'front_hooks' in fields:
                fields['front_hooks'] = ''.join(fields['front_hooks'])
            else:
                fields['front_hooks'] = ''

            if 'back_hooks' in fields:
                fields['back_hooks'] = ''.join(fields['back_hooks'])
            else:
                fields['back_hooks'] = ''
            print(''.join(sorted(word)), word, *fields.values(),
                  sep="\t", flush=True)


def __main__():
    parser = ArgumentParser()
    parser.add_argument("wordlist")
    parser.add_argument("-o", "--output")

    args = parser.parse_args()

    build_lexicon(args.wordlist)


if __name__ == "__main__":
    __main__()
