from argparse import ArgumentParser
from collections import Counter
import pickle
from functools import lru_cache


FREQUENCIES = {
    "A": 9,
    "B": 2,
    "C": 2,
    "D": 4,
    "E": 12,
    "F": 2,
    "G": 3,
    "H": 2,
    "I": 9,
    "J": 1,
    "K": 1,
    "L": 4,
    "M": 2,
    "N": 6,
    "O": 8,
    "P": 2,
    "Q": 1,
    "R": 6,
    "S": 4,
    "T": 6,
    "U": 4,
    "V": 2,
    "W": 2,
    "X": 1,
    "Y": 2,
    "Z": 1,
    "?": 2,
}


@lru_cache()
def combinations(n, k):
    """Return the binomial coefficient (n, k).
    """
    if n - k < k:
        return combinations(n, n - k)
    num, dem = 1, 1
    for i in range(1, n - k + 1):
        num *= n - i + 1
        dem *= i
    return num // dem


def compute_probability(word):
    desirable_racks = 1
    counts = Counter(word)
    for letter, count in counts.items():
        desirable_racks *= combinations(FREQUENCIES[letter], count)

    total_racks = combinations(100, len(word))

    return desirable_racks / total_racks


def build_lexicon(wordlist):

    with open(wordlist) as words:
        lexicon = {}
        for line in words.readlines():
            word, defn = line.strip().split("\t")
            lexicon[word] = {}
            lexicon[word]["alphagram"] = "".join(sorted(word))
            lexicon[word]["word"] = word
            lexicon[word]["definition"] = defn

        for word in lexicon:
            if word[1:] in lexicon:
                # print("Front hook: %s -> %s" % (word[1:], word))
                front_hooks = lexicon[word[1:]].get("front_hooks", [])
                lexicon[word[1:]]["front_hooks"] = front_hooks + [word[0]]
                lexicon[word]["front_inner_hook"] = True
            if word[:-1] in lexicon:
                """
                if word[-1] != "S":
                    print("Back hook:  %s -> %s" % (word[:-1], word))
                    """
                back_hooks = lexicon[word[:-1]].get("backhooks", [])
                lexicon[word[:-1]]["back_hooks"] = back_hooks + [word[-1]]
                lexicon[word]["back_inner_hook"] = True

            lexicon[word]["length"] = len(word)
            lexicon[word]["vowels"] = len([c for c in word if c in "AEIOU"])
            lexicon[word]["pct_vowels"] = (
                100 * lexicon[word]["vowels"] // len(word)
            )
            lexicon[word]["consonants"] = len(word) - lexicon[word]["vowels"]
            lexicon[word]["pct_consonants"] = 100 - lexicon[word]["pct_vowels"]

        for word, fields in lexicon.items():
            if "front_hooks" in fields:
                fields["front_hooks"] = "".join(fields["front_hooks"])
            else:
                fields["front_hooks"] = ""

            if "back_hooks" in fields:
                fields["back_hooks"] = "".join(fields["back_hooks"])
            else:
                fields["back_hooks"] = ""

            if "front_inner_hook" not in fields:
                fields["front_inner_hook"] = False

            if "back_inner_hook" not in fields:
                fields["back_inner_hook"] = False

        return lexicon


def __main__():
    parser = ArgumentParser()
    parser.add_argument("wordlist")
    parser.add_argument("-o", "--output")

    args = parser.parse_args()

    lexicon = build_lexicon(args.wordlist)
    if args.output:
        with open(args.output, "wb") as out:
            pickle.dump(lexicon, out)


if __name__ == "__main__":
    __main__()
