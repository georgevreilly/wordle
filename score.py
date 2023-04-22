#!/usr/bin/env python3

"""Validate ParsedGuesses.score against all results in README.md"""

import re

from wordle import ParsedGuesses


GAME_RE = re.compile(r"""^\*.+`(?P<guess_scores>[^`]+)`[^`]+`(?P<actual>[A-Z]+)`""")

failures = []
with open("README.md") as f:
    for line in f.readlines():
        if line.startswith("* ") and line.count("`") == 4:
            m = GAME_RE.match(line.strip())
            assert m is not None
            actual = m.group("actual")
            guess_scores = m.group("guess_scores").split()
            print(f"{actual=}: {guess_scores=}")
            for gs in guess_scores:
                guess, score = gs.split("=")
                computed = ParsedGuesses.score(actual, guess)
                print(f"\t{guess=} {score=} {computed=} {'Correct' if computed==score else 'Wrong'}")
                if computed != score:
                    failures.append((actual, guess, score, computed))

print(f"{failures=}")
