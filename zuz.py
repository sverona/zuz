import re
import string
import pickle
import itertools as it
from argparse import ArgumentParser
from csv import DictReader


def num_vowels(word):
    return len(re.findall("[AEIOU]", word))


def num_consonants(word):
    return len(word) - num_vowels(word)


def point_value(word):
    points = [
        1,
        3,
        3,
        2,
        1,
        4,
        2,
        4,
        1,
        8,
        5,
        1,
        3,
        1,
        1,
        3,
        10,
        1,
        1,
        1,
        1,
        4,
        4,
        8,
        4,
        10,
    ]

    return sum(
        point * word.count(letter)
        for point, letter in zip(points, string.ascii_uppercase)
    )


def parse_range(range_):
    # TODO do this properly, returning a predicate
    # TODO handle commas
    limits = range_.split("-")
    if limits[0] == "":
        limits[0] = 0
    if limits[-1] == "":
        limits[-1] = 10 ** 12
    limits = [int(lim) for lim in limits]

    return range(min(limits), max(limits) + 1)


def clean_pattern(pattern):
    """
    """
    if pattern:
        good_chars = string.ascii_letters + "?*-[]"
        cleaned_pattern = "".join(ch for ch in pattern if ch in good_chars)
    else:
        cleaned_pattern = ""

    return cleaned_pattern.upper()


def sort_pattern(pattern):
    """
    """
    token_regex = re.compile("(\\[[A-Z-]*\\]|\\?|[A-Z]|\\*)")

    return "".join(sorted(re.split(token_regex, pattern)))


def pattern_to_regex(pattern):
    """
    """

    # TODO Smarten this up (on a per-letter basis.)
    range_regex = re.compile("(\\?|\\*|\\[[A-Z-]*\\])")
    ranges = re.findall(range_regex, pattern)
    ranges = ["[A-Z]" if range_ == "?" else range_ for range_ in ranges]
    non_ranges = re.sub(range_regex, "", pattern)

    def insert_ranges(pat, ranges, positions):
        pat_with_ranges = ""
        last_pos = 0

        for pos, range_ in zip(sorted(positions), ranges):
            substr = pat[last_pos:pos]
            pat_with_ranges += substr + range_
            last_pos = pos

        return pat_with_ranges + pat[last_pos:]

    if not ranges:
        return pattern
    else:
        patterns = [
            insert_ranges(non_ranges, permuted_ranges, pos)
            for permuted_ranges in it.permutations(ranges)
            for pos in it.product(range(len(non_ranges) + 1), repeat=len(ranges))
        ]

        patterns = list(set(patterns))

        return f"({'|'.join(patterns)})"


def __main__():
    parser = ArgumentParser(description="")
    parser.add_argument("-2", action="append_const", dest="length", const=2)
    parser.add_argument("-3", action="append_const", dest="length", const=3)
    parser.add_argument("-4", action="append_const", dest="length", const=4)
    parser.add_argument("-5", action="append_const", dest="length", const=5)
    parser.add_argument("-6", action="append_const", dest="length", const=6)
    parser.add_argument("-7", action="append_const", dest="length", const=7)
    parser.add_argument("-8", action="append_const", dest="length", const=8)
    parser.add_argument("-9", action="append_const", dest="length", const=9)

    parser.add_argument("-a", "--anagram", action="store_true")
    parser.add_argument("-s", "--subanagram", action="store_true")
    parser.add_argument("-e", "--exact", action="store_true")

    parser.add_argument("-d", "--dict", "--dictionary", default="NWL2018")

    parser.add_argument("-l", "--length")
    parser.add_argument("-v", "--num-vowels", "--vowels")
    parser.add_argument("-c", "--num-consonants", "--consonants")
    parser.add_argument("-V", "--percent-vowels", "--pct-vowels")
    parser.add_argument("-C", "--percent-consonants", "--pct-consonants")
    parser.add_argument("-p", "--probability-order")
    parser.add_argument("-P", "--playability-order")
    parser.add_argument("--point-value", "--score")

    parser.add_argument("--long", action="store_true")

    parser.add_argument("pattern", metavar="PATTERN")

    args = parser.parse_args()

    pattern = clean_pattern(args.pattern)

    if args.exact:
        regex = pattern
        regex = re.sub("\?", "[A-Z]", regex)
        regex = re.sub("\*", "[A-Z]*", regex)
    elif args.subanagram:
        pattern = sort_pattern(pattern)
        regex = re.sub("\*", "", pattern)
        regex = re.sub("(.)", "\\1[A-Z]*", regex)
        regex = re.sub("\?", "[A-Z]", regex)
        regex = re.sub("^", "[A-Z]*", regex)
    else:
        pattern = sort_pattern(pattern)
        regex = pattern_to_regex(pattern)

    regex = f"^{regex}\\b"

    with open(f"dicts/{args.dict}.pickle", "rb") as infile:
        words = pickle.load(infile)

        matching_words = {
            word: values
            for word, values in words.items()
            if re.match(regex, values["alphagram"])
        }

        def select(words, field, range_):
            if not range_:
                return words

            if isinstance(range_, str):
                range_ = parse_range(range_)
            return {
                alphagram: word
                for alphagram, word in words.items()
                if int(field(word)) in range_
            }

        matching_words = select(
            matching_words, lambda word: word["length"], args.length
        )
        matching_words = select(
            matching_words, lambda word: word["num_vowels"], args.num_vowels
        )
        matching_words = select(
            matching_words, lambda word: word["num_consonants"], args.num_consonants
        )
        matching_words = select(
            matching_words, lambda word: word["percent_vowels"], args.percent_vowels
        )
        matching_words = select(
            matching_words,
            lambda word: word["percent_consonants"],
            args.percent_consonants,
        )

        if args.point_value:
            range_ = parse_range(args.point_value)
            matching_words = {
                alphagram: word
                for alphagram, word in matching_words.items()
                if point_value(alphagram) in range_
            }

        for alphagram, word in matching_words.items():
            if args.long:
                print("\t".join(word.values()))
            else:
                print("\t".join([word["alphagram"], word["word"], word["definition"]]))


if __name__ == "__main__":
    __main__()
