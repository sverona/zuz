import re
import string
import itertools as it
from argparse import ArgumentParser


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
    parser.add_argument("-2", action="store_const", dest="length", const=2)
    parser.add_argument("-3", action="store_const", dest="length", const=3)
    parser.add_argument("-4", action="store_const", dest="length", const=4)
    parser.add_argument("-5", action="store_const", dest="length", const=5)
    parser.add_argument("-6", action="store_const", dest="length", const=6)
    parser.add_argument("-7", action="store_const", dest="length", const=7)
    parser.add_argument("-8", action="store_const", dest="length", const=8)
    parser.add_argument("-9", action="store_const", dest="length", const=9)

    parser.add_argument("-a", "--anagram", action="store_true")
    parser.add_argument("-s", "--subanagram", action="store_true")
    parser.add_argument("-e", "--exact", action="store_true")

    parser.add_argument("-d", "--dict", "--dictionary")

    parser.add_argument("-l", "--length")
    parser.add_argument("-v", "--num-vowels", "--vowels")
    parser.add_argument("-c", "--num-consonants", "--consonants")
    parser.add_argument("-V", "--percent-vowels", "--pct-vowels")
    parser.add_argument("-C", "--percent-consonants", "--pct-consonants")
    parser.add_argument("-p", "--probability-order")
    parser.add_argument("-P", "--playability-order")
    parser.add_argument("--point-value", "--score")

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
    print(regex)

    with open("dicts/NWL2018.tsv") as lexicon:
        words = lexicon.read().splitlines()

        matching_words = [
            word.split("\t")[0] for word in words if re.match(regex, word)
        ]

        if args.length:
            range_ = parse_range(args.length)
            matching_words = [word for word in matching_words if len(word) in range_]
        if args.num_vowels:
            range_ = parse_range(args.num_vowels)
            matching_words = [
                word for word in matching_words if num_vowels(word) in range_
            ]
        if args.num_consonants:
            range_ = parse_range(args.num_consonants)
            matching_words = [
                word for word in matching_words if num_consonants(word) in range_
            ]
        if args.percent_vowels:
            range_ = parse_range(args.percent_vowels)
            matching_words = [
                word
                for word in matching_words
                if num_vowels(word) // len(word) * 100 in range_
            ]
        if args.percent_consonants:
            range_ = parse_range(args.percent_consonants)
            matching_words = [
                word
                for word in matching_words
                if num_consonants(word) // len(word) * 100 in range_
            ]
        if args.point_value:
            range_ = parse_range(args.point_value)
            matching_words = [
                word for word in matching_words if point_value(word) in range_
            ]

        for word in matching_words:
            print(word)


if __name__ == "__main__":
    __main__()
