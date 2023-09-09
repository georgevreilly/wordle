#!/usr/bin/env python3

import argparse
import os

DICT_FILE = "/usr/share/dict/words"
# From github.com/dwyl/english-words
ALPHA_FILE = os.path.join(os.path.dirname(__file__), "words_alpha.txt")

parser = argparse.ArgumentParser(description="Spelling Bee Finder")
parser.set_defaults(
    word_file=ALPHA_FILE,
)
parser.add_argument(
    "letters",
    help="Seven uppercase letters. Center (mandatory) letter first."
)
parser.add_argument(
    "--dict", "-d",
    action="store_const", const=DICT_FILE, dest="word_file",
    help="Use %(const)s")
parser.add_argument(
    "--alpha", "-a",
    action="store_const", const=ALPHA_FILE, dest="word_file",
    help="Use %(const)s")
namespace = parser.parse_args()

center = namespace.letters[0]
others = {c for c in namespace.letters[1:]}
if len({c for c in namespace.letters}) != 7 or not all("A" <= c <= "Z" for c in namespace.letters):
    raise ValueError(f"Need 7 distinct uppercase letters for Spelling Bee: {namespace.letters!r}")


def print_list(label: str, lst: list[str]) -> None:
    print("\n{}:\n\t{}".format(label, "\n\t".join(lst)))


with open(namespace.word_file) as f:
    WORDS = [w.upper() for w in f.read().splitlines()]

pangrams = []
buzzes = []
for w in WORDS:
    if len(w) < 4:
        continue
    chars = {c.upper() for c in w}
    if center not in chars:
        continue
    if chars - others != {center}:
        continue
    if len(chars) == 7:
        pangrams.append(w)
    buzzes.append(w)

buzzes.sort()
previous = [buzzes[0]]

for buzz in buzzes[1:]:
    if buzz[:2] != previous[0][:2]:
        print_list(previous[0][:2], previous)
        previous = []
    previous.append(buzz)

print_list(previous[0][:2], previous)
print_list("Pangrams", sorted(pangrams))
