#!/usr/bin/env python3

"""Validate WordleGuesses.score against all results in games.md"""

from __future__ import annotations

import argparse
import re

from common import ANSWERS_FILE, GAMES_FILE, WORD_FILE, GameResult, read_vocabulary
from wordle import WordleGuesses


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score Validator")
    parser.set_defaults(
        game=0,
    )
    parser.add_argument("--game", "-g", type=int, help="Game to start with; e.g., 723")
    return parser.parse_args()


# These answers to actual games were not in "answers.txt"
EXCEPTIONAL_ANSWERS = {"GUANO", "SNAFU", "BALSA", "KAZOO"}


def check_scores(first_game: int) -> list:
    vocabulary = read_vocabulary(WORD_FILE)
    answers = set(read_vocabulary(ANSWERS_FILE))
    failures = []
    game_results = GameResult.parse_file(GAMES_FILE)
    for gr in game_results:
        if first_game > gr.game_id:
            continue

        print(
            f"{gr.game_id}: {gr.answer}: {' '.join(str(gs) for gs in gr.guess_scores)}"
        )
        # TODO: throw an error for OUGHT=..g.. GRAVE=gr..e MERGE=..rGE (the 'e' in GRAVE)
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
        parts = parsed_guesses.string_parts()
        gs2 = parts.pop("guess_scores")
        pieces = ", ".join(f"{k}={v}" for k, v in parts.items())
        print(f"\tWordleGuesses:\t{pieces}\n\t\t\tguess_scores: {gs2}")
        if any(parsed_guesses.mask):
            pattern = re.compile("".join(m or "." for m in parsed_guesses.mask))
            word_list = [w for w in vocabulary if pattern.fullmatch(w)]
        else:
            word_list = vocabulary
        eligible = parsed_guesses.find_eligible(word_list)
        plausible = {p for p in eligible if p in answers}
        assert gr.answer in eligible, f"{eligible=}"
        if gr.answer not in EXCEPTIONAL_ANSWERS:
            assert gr.answer in answers, f"{gr.game_id}: {gr.answer} in known answers"
        if "yields" == gr.verb:
            # I previously decided that any other possibilities would never be used
            assert len(eligible) >= 1, f"{gr.game_id} yields: {eligible}"
            assert len(plausible) == 1, f"{gr.answer} == {plausible!r}"
        elif "includes" == gr.verb:
            assert len(eligible) > 1, f"{gr.game_id} includes: {eligible}"
            assert (
                len(plausible) > 1 or gr.answer in EXCEPTIONAL_ANSWERS
            ), f"{gr.answer} in {plausible}"
        else:
            raise ValueError(f"Unknown {gr.verb}")
        implausible = " ".join(sorted(r for r in eligible if r not in plausible))
        others = " ".join(sorted(plausible - {gr.answer}))
        print(
            f"\t{gr.verb}={gr.answer}, plausible=[{others}], "
            f"implausible=[{implausible}]"
        )
    return failures


def main() -> int:
    namespace = parse_args()
    failures = check_scores(namespace.game)
    if failures:
        print(f"{failures=}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
