#!/usr/bin/env python3

"""Generate statistics about Wordle Start Words"""

import argparse
import os

from collections import defaultdict
from operator import itemgetter
from typing import Iterable

WORDLE_LEN = 5
WORD_FILE = os.path.join(os.path.dirname(__file__), "wordle.txt")

parser = argparse.ArgumentParser(description="Wordle Start Words")
parser.set_defaults(
    # word_file="/usr/share/dict/words",
    word_file=WORD_FILE,
    len=WORDLE_LEN,
    topmost=50,
    top_per_letter=20,
    threshold_score=0.30,
)
namespace = parser.parse_args()

AtoZ = [chr(c) for c in range(ord("A"), ord("Z") + 1)]


def rev_sort_by_count(pairs: Iterable[tuple[str, int]]) -> list[tuple[str, int]]:
    return sorted(pairs, reverse=True, key=itemgetter(1))


with open(namespace.word_file) as f:
    WORDS = [w.upper() for w in f.read().splitlines() if len(w) == namespace.len]

print("Letter Frequencies")
letter_counts = {c: 0 for c in AtoZ}
total_letters = len(WORDS) * namespace.len
pos_pop = {c: [0 for _ in range(namespace.len)] for c in AtoZ}

for w in WORDS:
    for i, c in enumerate(w):
        letter_counts[c] += 1
        pos_pop[c][i] += 1

frequencies = {
    letter: count / total_letters for letter, count
    in rev_sort_by_count(letter_counts.items())
}

for i, (l, p) in enumerate(frequencies.items()):
    print(f"{l}: {p:.4f}  ", end="")
    if i % 6 == WORDLE_LEN:
        print()
print("\n")

print("   Freq% Order      1    2    3    4    5")
for letter, positions in pos_pop.items():
    order = "".join(
        [
            str(x[1])
            for x in sorted(
                [(n, i) for i, n in enumerate(positions, 1)],
                reverse=True,
                key=itemgetter(0),
            )
        ]
    )
    positions2 = " ".join(f"{p:4}" for p in positions)
    print(f"{letter}: {100.0 * frequencies[letter]:5.2f} {order} - {positions2}")
print()

start_words = defaultdict(list)
alpha_words: dict[str, list[tuple[str, int]]] = {c: [] for c in AtoZ}

for w in WORDS:
    letters = {c for c in w}
    if len(letters) == namespace.len:
        score = sum(letter_counts[c] for c in w)
        score += sum(pos_pop[c][i] for i, c in enumerate(w))
        # TODO: use ngram popularity in score
        start_words["".join(sorted(letters))].append((w, score))
        alpha_words[w[0]].append((w, score))

print(f"{len(start_words)}/{len(WORDS)} words with {namespace.len} distinct letters")

print("Most popular sets of letters, best position first")
topwords = sorted(start_words.items(), reverse=True, key=lambda kv: kv[1][0][1])[
    : namespace.topmost
]
for i, x in enumerate(topwords, 1):
    anagrams = [f"{ws[0]}" for ws in sorted(x[1], reverse=True, key=itemgetter(1))]
    print(f"{i:2}: {' '.join(anagrams)}")

print("\n\nBest Start Words, weighted by position\n")
for letter in AtoZ:
    topwords2 = rev_sort_by_count(alpha_words[letter])[: namespace.top_per_letter]
    print(
        f"{letter}: {' '.join(ws[0] for ws in topwords2 if ws[1] >= namespace.threshold_score)}"
    )


def ngrams(n: int):
    counts: dict[str, int] = defaultdict(int)
    for w in WORDS:
        for i in range(namespace.len - n + 1):
            counts[w[i:i + n]] += 1
    ngram_counts = rev_sort_by_count(counts.items())
    prefixes: dict[str, list[tuple[str, int]]] = {c: [] for c in AtoZ}
    suffixes: dict[str, list[tuple[str, int]]] = {c: [] for c in AtoZ}
    for nc in ngram_counts:
        prefixes[nc[0][0]].append(nc)
        suffixes[nc[0][-1]].append(nc)
    for c in AtoZ:
        prefixes[c] = rev_sort_by_count(prefixes[c])
        suffixes[c] = rev_sort_by_count(suffixes[c])
    return ngram_counts, prefixes, suffixes


print("\n2-ngrams")
ngrams2, prefixes, suffixes = ngrams(2)
for i in range(1, 10 + 1):
    print(f"{i:2}: {sum(1 if nc[1] == i else 0 for nc in ngrams2)}, ", end="")
print("\n")

for i, nc in enumerate(nc for nc in ngrams2 if nc[1] >= 100):
    print(f"{nc[0]}: {nc[1]:3}  ", end="")
    if i % 8 == 7:
        print()
print("\n")

for c in AtoZ:
    print(f"{c}:\t{' '.join([nc[0] for nc in prefixes[c] if nc[1] >= 50])}")
    print(f"\t{' '.join([nc[0] for nc in suffixes[c] if nc[1] >= 50])}")
