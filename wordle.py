#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(description="Wordle Finder")
parser.set_defaults(
    word_file="/usr/share/dict/words",
    len=5,
)
parser.add_argument("--verbose", "-v", action="store_true", help="Show all the steps")
parser.add_argument(
    "guess",
    nargs="+",
    metavar="WORD=guess",
    help="Examples: 'ARISE=.r.se' 'ROUTE=R.u.e' 'RULES=Ru.eS'",
)
namespace = parser.parse_args()


def debug(s):
    if namespace.verbose:
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
        debug(f"!Valid: {w}")
    elif letters & invalid:
        debug(f"Invalid: {w}")
    elif any(m is not None and c != m for c, m in zip(w, mask)):
        debug(f"!Mask: {w}")
    elif any(c in ws for c, ws in zip(w, wrong_spot)):
        debug(f"WrongSpot: {w}")
    else:
        choices.append(w)
        debug(f"Got: {w}")

print("\n".join(choices))
