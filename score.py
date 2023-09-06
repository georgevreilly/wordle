#!/usr/bin/env python3

"""Validate WordleGuesses.score against all results in games.md"""

import argparse
import os
import re

from wordle import GuessScore, WordleGuesses, read_vocabulary

GAME_RE = re.compile(
    r"""^\* (?P<game>[0-9]+): `(?P<guess_scores>[^`]+)`(?P<verb>[^`]+)`(?P<answer>[A-Z]+)`""")
GAMES = os.path.join(os.path.dirname(__file__), "games.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score Validator")
    parser.set_defaults(
        game=0,
    )
    parser.add_argument(
        "--game", "-g", type=int, help="Game to start with; e.g., 723")
    return parser.parse_args()


def check_scores(first_game: int) -> list:
    vocabulary = read_vocabulary()
    failures = []
    with open(GAMES) as f:
        for line in f.read().splitlines():
            if line.startswith("* ") and line.count("`") == 4:
                m = GAME_RE.match(line)
                assert m is not None
                game = int(m.group("game"))
                answer = m.group("answer")
                verb = m.group("verb").strip().strip('*')
                guess_scores = [GuessScore.make(gs) for gs in m.group("guess_scores").split()]
                if first_game > game:
                    continue

                print(f"{game}: {answer}: {' '.join(str(gs) for gs in guess_scores)}")
                for gs in guess_scores:
                    computed = WordleGuesses.score(answer, gs.guess)
                    verdict = "✅ Correct" if computed == gs.score else "❌ Wrong!"
                    print(f"\tguess={gs.guess} score={gs.score} {computed=} ‹{gs.emojis()}›  {verdict}")
                    if computed != gs.score:
                        failures.append((answer, gs.guess, gs.score, computed))

                parsed_guesses = WordleGuesses.parse(guess_scores)
                print(f"\t{parsed_guesses}")
                eligible = parsed_guesses.find_eligible(vocabulary)
                choices = " ".join(f"«{e}»" if e == answer else e for e in eligible)
                print(f"\t{verb}: {choices}")
                assert answer in eligible
                if "yields" == verb:
                    # I previously decided that any other possibilities would never be used
                    assert len(eligible) >= 1, f"{game} yields: {eligible}"
                elif "includes" == verb:
                    assert len(eligible) > 1, f"{game} includes: {eligible}"
                else:
                    raise ValueError(f"Unknown {verb}")
    return failures


def main() -> int:
    namespace = parse_args()
    failures = check_scores(namespace.game)
    if failures:
        print(f"{failures=}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
