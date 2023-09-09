#!/usr/bin/env python3

"""Validate WordleGuesses.score against all results in games.md"""

import argparse

from common import GAMES_FILE, GameResult, read_vocabulary
from wordle import WordleGuesses


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score Validator")
    parser.set_defaults(
        game=0,
    )
    parser.add_argument("--game", "-g", type=int, help="Game to start with; e.g., 723")
    return parser.parse_args()


def check_scores(first_game: int) -> list:
    vocabulary = read_vocabulary()
    failures = []
    game_results = GameResult.parse_game_results(GAMES_FILE)
    for gr in game_results:
        if first_game > gr.game_id:
            continue

        print(
            f"{gr.game_id}: {gr.answer}: {' '.join(str(gs) for gs in gr.guess_scores)}"
        )
        for gs in gr.guess_scores:
            computed = WordleGuesses.score(gr.answer, gs.guess)
            verdict = "✅ Correct" if computed == gs.score else "❌ Wrong!"
            print(
                f"\tguess={gs.guess} score={gs.score} {computed=} "
                f"‹{gs.emojis()}›  {verdict}"
            )
            if computed != gs.score:
                failures.append((gr.answer, gs.guess, gs.score, computed))

        parsed_guesses = WordleGuesses.parse(gr.guess_scores)
        print(f"\t{parsed_guesses}")
        eligible = parsed_guesses.find_eligible(vocabulary)
        choices = " ".join(f"«{e}»" if e == gr.answer else e for e in eligible)
        print(f"\t{gr.verb}: {choices}")
        assert gr.answer in eligible
        if "yields" == gr.verb:
            # I previously decided that any other possibilities would never be used
            assert len(eligible) >= 1, f"{gr.game_id} yields: {eligible}"
        elif "includes" == gr.verb:
            assert len(eligible) > 1, f"{gr.game_id} includes: {eligible}"
        else:
            raise ValueError(f"Unknown {gr.verb}")
    return failures


def main() -> int:
    namespace = parse_args()
    failures = check_scores(namespace.game)
    if failures:
        print(f"{failures=}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
