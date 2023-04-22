#!/usr/bin/env python3

"""Validate ParsedGuesses.score against all results in README.md"""

import re

from wordle import ParsedGuesses, read_vocabulary


GAME_RE = re.compile(r"""^\*.+`(?P<guess_scores>[^`]+)`(?P<verb>[^`]+)`(?P<actual>[A-Z]+)`""")

vocabulary = read_vocabulary()
failures = []
with open("README.md") as f:
    for line in f.readlines():
        if line.startswith("* ") and line.count("`") == 4:
            m = GAME_RE.match(line.strip())
            assert m is not None
            actual = m.group("actual")
            verb = m.group("verb")
            guess_scores = m.group("guess_scores").split()
            print(f"{actual=}: {guess_scores=}")
            for gs in guess_scores:
                guess, score = gs.split("=")
                computed = ParsedGuesses.score(actual, guess)
                print(f"\t{guess=} {score=} {computed=} {'Correct' if computed==score else 'Wrong'}")
                if computed != score:
                    failures.append((actual, guess, score, computed))

            eligible = ParsedGuesses.parse(guess_scores).find_eligible(vocabulary)
            assert actual in eligible
            if "yields" in verb:
                # I previously decided that any other possibilities would never be used
                assert len(eligible) >= 1, f"yields: {eligible}"
            elif "includes" in verb:
                assert len(eligible) > 1, f"includes: {eligible}"

print(f"{failures=}")
