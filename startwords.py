#!/usr/bin/env python3

import argparse
from collections import defaultdict
from operator import itemgetter

parser = argparse.ArgumentParser(description="Wordle Start Words")
parser.set_defaults(
    # word_file="/usr/share/dict/words",
    word_file="wordle.txt",
    len=5,
    topmost=50,
    top_per_letter=20,
    threshold_score=0.30,
)
namespace = parser.parse_args()

AtoZ = [chr(c) for c in range(ord("A"), ord("Z") + 1)]


with open(namespace.word_file) as f:
    WORDS = [w.upper() for w in f.read().splitlines() if len(w) == namespace.len]

letter_counts = {c: 0 for c in AtoZ}
total_letters = 0
pos_pop = {c: [0 for _ in range(namespace.len)] for c in AtoZ}

for w in WORDS:
    total_letters += len(w)
    for i, c in enumerate(w):
        letter_counts[c] += 1
        pos_pop[c][i] += 1

frequencies = {
    l: c / total_letters
    for l, c in sorted(letter_counts.items(), reverse=True, key=itemgetter(1))
}

for i, (l, p) in enumerate(frequencies.items()):
    print(f"{l}: {p:.4f}  ", end="")
    if i % 6 == 5: print()
print("\n")

print("   Freq   Order      1    2    3    4    5")
for letter, positions in pos_pop.items():
    order = "".join([str(x[1]) for x in sorted([(w, i) for i, w in enumerate(positions, 1)], reverse=True, key=itemgetter(0))])
    positions = " ".join(f"{p:4}" for p in positions)
    print(f"{letter}: {frequencies[letter]:.4f} {order} - {positions}")
print()

start_words = defaultdict(list)
alpha_words = {c: [] for c in AtoZ}

for w in WORDS:
    letters = {c for c in w}
    if len(letters) == namespace.len:
        score = sum(letter_counts[c] for c in w) / total_letters
        score += sum(pos_pop[c][i] for i, c in enumerate(w)) / total_letters
        start_words["".join(sorted(letters))].append((w, score))
        alpha_words[w[0]].append((w, score))

print(f"{len(start_words)}/{len(WORDS)} words with {namespace.len} distinct letters")
topwords = sorted(start_words.items(), reverse=True, key=lambda kv: kv[1][0][1])[
    : namespace.topmost
]
for i, x in enumerate(topwords, 1):
    anagrams = [ws[0] for ws in x[1]]
    print(f"{i:2}: {' '.join(anagrams)}")

print()

for letter in AtoZ:
    topwords = sorted(alpha_words[letter], reverse=True, key=itemgetter(1))[
        : namespace.top_per_letter
    ]
    print(
        f"{letter}: {' '.join(ws[0] for ws in topwords if ws[1] >= namespace.threshold_score)}"
    )
