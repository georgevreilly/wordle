#!/usr/bin/env python3

"""Validate WordleGuesses.score against all results in games.md"""

from __future__ import annotations

import argparse
import os
import re

from common import ANSWERS_FILE, GAMES_FILE, WORD_FILE, GameResult, read_vocabulary
from wordle import WordleGuesses


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Score Validator for {os.path.basename(GAMES_FILE)}",
        epilog="Use a negative argument (such as -3) to handle the last N games",
    )
    parser.set_defaults(
        first_game=0,
        last_game=9999,
    )
    parser.add_argument("--first-game", "-g", type=int, help="Game to start with; e.g., 723")
    parser.add_argument("--last-game", "-l", type=int, help="Game to end with; e.g., 726")
    namespace, argv = parser.parse_known_args()
    if argv:
        arg = argv[0]
        if arg[0] == "-" and arg[1:].isdigit():
            namespace.first_game = int(arg)
        else:
            raise ValueError(f"Expected negative integer, such as -2: {arg=}")
    return namespace


# These answers to actual games were not in "answers.txt"
EXCEPTIONAL_ANSWERS = {
    "GUANO",
    "SNAFU",
    "BALSA",
    "KAZOO",
    "LASER",
    "PIOUS",
    "BEAUT",
    "MOMMY",
    "PRIMP",
    "UVULA",
    "ATLAS",
    "SQUID",
    "RUMBA",
    "INDIE",
    "SPATE",
    "SUEDE",
    "GRIFT",
    "TAUPE",
    "ATRIA",
    "NERVY",
    "LORIS",
    "TIZZY",
    "GOFER",
    "KEFIR",
    "KNELL",
    "MATTE",
    "GIZMO",
    "TINGE",
    "COLIC",
    "MUGGY",
    "SITAR",
    "OOMPH",
    "MOOCH",
}


def check_scores(first_game: int, last_game: int) -> list:
    vocabulary = read_vocabulary(WORD_FILE)
    answers = set(read_vocabulary(ANSWERS_FILE))
    game_failures = []
    game_results = GameResult.parse_file(GAMES_FILE)
    if first_game < 0:
        game_results = game_results[first_game:]
    else:
        game_results = [gr for gr in game_results if first_game <= gr.game_id <= last_game]
    for gr in game_results:
        print(f"{gr.game_id}: {gr.answer}: {' '.join(str(gs) for gs in gr.guess_scores)}")
        score_failures = []
        for gs in gr.guess_scores:
            computed = WordleGuesses.score(gr.answer, gs.guess)
            verdict = (
                "\033[0;32m✅ Correct\033[0m"
                if computed == gs.score
                else "\033[0;31m❌ Wrong!\033[0m"
            )
            print(f"\tguess={gs.guess} score={gs.score} {computed=} ‹{gs.emojis()}›  {verdict}")
            if computed != gs.score:
                score_failures.append((gr.answer, gs.guess, gs.score, computed))

        assert not score_failures, f"{score_failures=}"
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
            assert gr.answer in answers, f"{gr.game_id}: {gr.answer} not in known answers"
        if "yields" == gr.verb:
            # I previously decided that any other possibilities would never be used
            assert len(eligible) >= 1, f"{gr.game_id} yields: {eligible}"
            assert len(plausible) == 1 or gr.answer in EXCEPTIONAL_ANSWERS, (
                f"{gr.answer} == {plausible!r}"
            )
        elif "includes" == gr.verb:
            assert len(eligible) > 1, f"{gr.game_id} includes: {eligible}"
            assert len(plausible) > 1 or gr.answer in EXCEPTIONAL_ANSWERS, (
                f"{gr.answer} in {plausible}"
            )
        else:
            raise ValueError(f"Unknown {gr.verb}")
        implausible = " ".join(sorted(r for r in eligible if r not in plausible))
        others = " ".join(sorted(plausible - {gr.answer}))
        print(f"\t{gr.verb}={gr.answer}, plausible=[{others}], implausible=[{implausible}]")
        game_failures.extend(score_failures)

    return game_failures


def main() -> int:
    namespace = parse_args()
    game_failures = check_scores(namespace.first_game, namespace.last_game)
    if game_failures:
        print(f"{game_failures=}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
