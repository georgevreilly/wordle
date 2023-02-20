#!/usr/bin/env python3

import argparse
from collections import defaultdict
from operator import itemgetter

parser = argparse.ArgumentParser(description="Wordle Start Words")
parser.set_defaults(
    # word_file="/usr/share/dict/words",
    word_file="wordle.txt",
    len=5,
    topmost=30,
)
namespace = parser.parse_args()

# https://pi.math.cornell.edu/~mec/2003-2004/cryptography/subs/frequencies.html
LETTER_PROBABILITIES = {
    "E": 12.02,
    "T": 9.10,
    "A": 8.12,
    "O": 7.68,
    "I": 7.31,
    "N": 6.95,
    "S": 6.28,
    "R": 6.02,
    "H": 5.92,
    "D": 4.32,
    "L": 3.98,
    "U": 2.88,
    "C": 2.71,
    "M": 2.61,
    "F": 2.30,
    "Y": 2.11,
    "W": 2.09,
    "G": 2.03,
    "P": 1.82,
    "B": 1.49,
    "V": 1.11,
    "K": 0.69,
    "X": 0.17,
    "Q": 0.11,
    "J": 0.10,
    "Z": 0.07,
}

AtoZ = range(ord('A'), ord('Z')+1)


with open(namespace.word_file) as f:
    WORDS = [w.upper() for w in f.read().splitlines() if len(w) == namespace.len]

letter_counts = {chr(c): 0 for c in AtoZ}
total_letters = 0
for w in WORDS:
    total_letters += len(w)
    for c in w:
        letter_counts[c] += 1

frequencies = {l: round(c/total_letters, 3)
               for l,c in sorted(letter_counts.items(), reverse=True, key=itemgetter(1))}
print(frequencies)

start_words = defaultdict(list)
alpha_words = {chr(c): [] for c in AtoZ}

for w in WORDS:
    letters = {c for c in w}
    if len(letters) == namespace.len:
        score = sum(letter_counts[c] for c in w) / total_letters
        start_words["".join(sorted(letters))].append((w, score))
        alpha_words[w[0]].append((w, score))

print(f"{len(start_words)}/{len(WORDS)} words with {namespace.len} distinct letters")
topwords = sorted(start_words.items(), reverse=True, key=lambda kv: kv[1][0][1])[:namespace.topmost]
for i, x in enumerate(topwords, 1):
    anagrams = [ws[0] for ws in x[1]]
    print(f"{i:2}: {' '.join(anagrams)}")

print()

for letter in (chr(c) for c in AtoZ):
    topwords = sorted(alpha_words[letter], reverse=True, key=itemgetter(1))[:namespace.topmost]
    print(f"{letter}: {' '.join(ws[0] for ws in topwords if ws[1] >= 0.30)}")

