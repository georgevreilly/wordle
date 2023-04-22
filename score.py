#!/usr/bin/env python3

"""Validate ParsedGuesses.score against all results in README.md"""

import re

from wordle import ParsedGuesses


GAME_RE = re.compile(r"""^\*.+`(?P<guess_results>[^`]+)`[^`]+`(?P<actual>[A-Z]+)`""")

failures = []
with open("README.md") as f:
    for line in f.readlines():
        if line.startswith("* ") and line.count("`") == 4:
            m = GAME_RE.match(line.strip())
            assert m is not None
            actual = m.group("actual")
            guess_results = m.group("guess_results").split()
            print(f"{actual=}: {guess_results=}")
            for gr in guess_results:
                guess, result = gr.split("=")
                score = ParsedGuesses.score(actual, guess)
                print(f"\t{guess=} {result=} {score=} {'Correct' if result==score else 'Wrong'}")
                if result != score:
                    failures.append((actual, guess, result, score))

print(f"{failures=}")
