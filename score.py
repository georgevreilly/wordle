#!/usr/bin/env python3

"""Validate WordleGuesses.score against all results in README.md"""

import re

from wordle import WordleGuesses, read_vocabulary


GAME_RE = re.compile(r"""^\*[^`]+`(?P<guess_scores>[^`]+)`(?P<verb>[^`]+)`(?P<actual>[A-Z]+)`""")

vocabulary = read_vocabulary()
failures = []
with open("README.md") as f:
    for line in f.read().splitlines():
        if line.startswith("* ") and line.count("`") == 4:
            m = GAME_RE.match(line)
            assert m is not None
            actual = m.group("actual")
            verb = m.group("verb")
            guess_scores = m.group("guess_scores").split()
            print(f"{actual}: {' '.join(guess_scores)}")
            for gs in guess_scores:
                guess, score = gs.split("=")
                computed = WordleGuesses.score(actual, guess)
                verdict = "✅ Correct" if computed==score else "❌ Wrong!"
                print(f"\t{guess=} {score=} {computed=}  {verdict}")
                if computed != score:
                    failures.append((actual, guess, score, computed))

            eligible = WordleGuesses.parse(guess_scores).find_eligible(vocabulary)
            assert actual in eligible
            if "yields" in verb:
                # I previously decided that any other possibilities would never be used
                assert len(eligible) >= 1, f"yields: {eligible}"
            elif "includes" in verb:
                assert len(eligible) > 1, f"includes: {eligible}"
            else:
                raise ValueError(f"Unknown {verb}")

if failures:
    print(f"{failures=}")
