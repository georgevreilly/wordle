#!/usr/bin/env python3

import re

from wordle import ParsedGuesses


GAME_RE = re.compile(r"""^\*.+`(?P<guess_results>[^`]+)`[^`]+`(?P<actual>[A-Z]+)`""")

failures = []
with open("README.md") as f:
    for line in f.readlines():
        if line.startswith("* ") and line.count("`") == 4:
            m = GAME_RE.match(line.strip())
            guess_results = m.group("guess_results").split()
            actual = m.group("actual")
            print(f"{actual=}: {guess_results=}")
            for gr in guess_results:
                guess, result = gr.split("=")
                score = ParsedGuesses.score(actual, guess)
                print(f"\t{guess=} {result=} {score=} {'Correct' if result==score else 'Wrong'}")
                if result != score:
                    failures.append((actual, guess, result, score))

print(f"{failures=}")
