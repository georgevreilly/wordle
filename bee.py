#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(description="Spelling Bee Finder")
parser.set_defaults(
    # word_file="/usr/share/dict/words",
    word_file="words_alpha.txt",  # github.com/dwyl/english-words
    min=4,
    verbose=0,
)
parser.add_argument(
    "--verbose", "-v", action="count", help="Show all the steps")
parser.add_argument(
    "letters",
    help="Seven letters. Center (mandatory) letter first."
)
namespace = parser.parse_args()

center = namespace.letters[0]
others = {c for c in namespace.letters[1:]}
if len({c for c in namespace.letters}) != 7 or not all("A" <= c <= "Z" for c in namespace.letters):
    raise ValueError(f"Need 7 distinct uppercase letters for Spelling Bee: {namespace.letters!r}")


def debug(s):
    if namespace.verbose:
        print(s)


def trace(s):
    if namespace.verbose >= 2:
        print(s)


with open(namespace.word_file) as f:
    WORDS = [w.upper() for w in f.read().splitlines()]


pangrams = []
buzzes = []
for w in WORDS:
    if len(w) < namespace.min:
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
        print("\n{}\n\t{}".format(previous[0][:2], "\n\t".join(previous)))
        previous = []
    previous.append(buzz)

print("\n{}\n\t{}".format(previous[0][:2], "\n\t".join(previous)))
print("\nPangrams:\n\t{}".format("\n\t".join(sorted(pangrams))))
