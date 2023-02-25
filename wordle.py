#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(description="Wordle Finder")
parser.set_defaults(
    # word_file="/usr/share/dict/words",
    word_file="wordle.txt",
    len=5,
    verbose=0,
)
parser.add_argument(
    "--verbose", "-v", action="count", help="Show all the steps")
parser.add_argument(
    "guess",
    nargs="+",
    metavar="WORD=guess",
    help="Examples: 'ARISE=.r.se' 'ROUTE=R.u.e' 'RULES=Ru.eS'",
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


def debug(s):
    if namespace.verbose:
        print(s)


def trace(s):
    if namespace.verbose >= 2:
        print(s)


with open(namespace.word_file) as f:
    WORDS = [w.upper() for w in f.read().splitlines() if len(w) == namespace.len]

# 'ADIEU=a.i..' 'CLOTH=c....'
# 'RAISE=r...e' 'CLOUT=.L...' 'NYMPH=.....' 'ELVER=EL.ER'
# 'GRAIL=.RA..' 'TRACK=.RAc.' 'CRAMP=CRA..' 'CRABS=CRA..' 'CRAZY=CRAZ.'
# 'ARISE=.r.se' 'ROUTE=R.u.e' 'RULES=Ru.eS'

invalid = set()  # Gray
valid = set()  # Green or Yellow
mask = [None] * namespace.len  # Exact match for position (Green)
wrong_spot = [set() for _ in range(namespace.len)]  # Wrong spot (Yellow)

for guess in namespace.guess:
    word, result = guess.split("=")
    assert len(word) == namespace.len
    assert len(result) == namespace.len
    for i, (w, r) in enumerate(zip(word, result)):
        assert "A" <= w <= "Z", "WORD should be uppercase"
        if "A" <= r <= "Z":
            valid.add(w)
            mask[i] = w
        elif "a" <= r <= "z":
            valid.add(w)
            wrong_spot[i].add(w)
        elif r == ".":
            if w not in valid:
                invalid.add(w)
        else:
            raise ValueError(f"Unexpected {r} for {w}")

debug(f"{invalid=}")
debug(f"{valid=}")
debug(f"{mask=}")
debug(f"{wrong_spot=}")

choices = []
for w in WORDS:
    letters = {c for c in w}
    if letters & valid != valid:
        trace(f"!Valid: {w}")
    elif letters & invalid:
        trace(f"Invalid: {w}")
    elif any(m is not None and c != m for c, m in zip(w, mask)):
        trace(f"!Mask: {w}")
    elif any(c in ws for c, ws in zip(w, wrong_spot)):
        trace(f"WrongSpot: {w}")
    else:
        choices.append(w)
        debug(f"Got: {w}")

print("\n".join(choices))
