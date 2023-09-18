#!/usr/bin/env python3

"""Validate WordleGuesses.score against all results in games.md"""

import argparse
import logging
import re
import string
from dataclasses import dataclass

from common import (
    GAMES_FILE,
    WORDLE_LEN,
    GameResult,
    GuessScore,
    TileState,
    dash_mask,
    letter_set,
    letter_sets,
    read_vocabulary,
)
from wordle import WordleGuesses


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score Validator")
    parser.set_defaults(
        first_game=0,
    )
    parser.add_argument(
        "--game",
        "-g",
        type=int,
        dest="first_game",
        help="Game to start with; e.g., 723",
    )
    return parser.parse_args()


@dataclass
class WordleGuessesLegacy:
    mask: list[str | None]  # Exact match for position (Green/Correct)
    valid: set[str]  # Green/Correct or Yellow/Present
    invalid: set[str]  # Black/Absent
    wrong_spot: list[set[str]]  # Wrong spot (Yellow/Present)
    guess_scores: list[GuessScore]

    @classmethod
    def parse(
        cls, guess_scores: list[GuessScore], invalid_kind: str
    ) -> "WordleGuessesLegacy":
        mask: list[str | None] = [None] * WORDLE_LEN
        valid: set[str] = set()
        invalid: set[str] = set()
        wrong_spot: list[set[str]] = [set() for _ in range(WORDLE_LEN)]

        for gs in guess_scores:
            for i in range(WORDLE_LEN):
                if gs.tiles[i] is TileState.CORRECT:
                    mask[i] = gs.guess[i]
                    valid.add(gs.guess[i])
                elif gs.tiles[i] is TileState.PRESENT:
                    wrong_spot[i].add(gs.guess[i])
                    valid.add(gs.guess[i])
                elif gs.tiles[i] is TileState.ABSENT:
                    if invalid_kind in {"set", "exclude"}:
                        invalid.add(gs.guess[i])
                    elif invalid_kind == "absent":
                        if gs.guess[i] not in valid:
                            invalid.add(gs.guess[i])

        if invalid_kind == "exclude":
            invalid -= valid

        return cls(mask, valid, invalid, wrong_spot, guess_scores)

    def is_eligible(self, word: str) -> bool:
        letters = {c for c in word}
        if letters & self.valid != self.valid:
            # Did not have the full set of green+yellow letters known to be valid
            logging.debug(f"!Valid: {word}")
            return False
        elif letters & self.invalid:
            # Invalid (black) letters are in the word
            logging.debug(f"Invalid: {word}")
            return False
        elif any(m is not None and c != m for c, m in zip(word, self.mask)):
            # Couldn't find all the green/correct letters
            logging.debug(f"!Mask: {word}")
            return False
        elif any(c in ws for c, ws in zip(word, self.wrong_spot)):
            # Found some yellow letters: valid letters in wrong position
            logging.debug(f"WrongSpot: {word}")
            return False
        else:
            # Potentially valid
            logging.info(f"Got: {word}")
            return True

    def find_eligible(self, vocabulary: list[str]) -> list[str]:
        return [w for w in vocabulary if self.is_eligible(w)]

    def __str__(self) -> str:
        mask = dash_mask(self.mask)
        valid = letter_set(self.valid)
        invalid = letter_set(self.invalid)
        wrong_spot = letter_sets(self.wrong_spot)
        unused = letter_set(set(string.ascii_uppercase) - self.valid - self.invalid)
        # _guess_scores = [", ".join(f"{gs}|{gs.emojis()}" for gs in self.guess_scores)]
        return (
            f"WordleGuesses({mask=}, {valid=}, {invalid=}, "
            f"{wrong_spot=}, {unused=})"
        )


def choices(answer: str, eligible: list[str]) -> str:
    return " ".join(f"«{e}»" if e == answer else e for e in eligible)


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
        parts = parsed_guesses.string_parts()
        gs2 = parts.pop("guess_scores")
        pieces = ", ".join(f"{k}={v}" for k, v in parts.items())
        print(f"\tWordleGuesses:\t{pieces}\n\t\t\tguess_scores: {gs2}")
        pattern = re.compile("".join(m or "." for m in parsed_guesses.mask))
        word_list = [w for w in vocabulary if pattern.fullmatch(w)]
        eligible = parsed_guesses.find_eligible(word_list)
        print(f"\t{gr.verb}: {choices(gr.answer, eligible)}")
        assert gr.answer in eligible
        if "yields" == gr.verb:
            # I previously decided that any other possibilities would never be used
            assert len(eligible) >= 1, f"{gr.game_id} yields: {eligible}"
        elif "includes" == gr.verb:
            assert len(eligible) > 1, f"{gr.game_id} includes: {eligible}"
        else:
            raise ValueError(f"Unknown {gr.verb}")
        if parsed_guesses.mask.count(None) == 2:
            print("\tKnow3")
        if mask2 := parsed_guesses.optimize():
            print(f"\tmask2={dash_mask(mask2)}")
        for i in range(WORDLE_LEN):
            if (inv1 := parsed_guesses.invalid[i]) != set():
                for j in range(WORDLE_LEN):
                    if (inv2 := parsed_guesses.invalid[j]) != set():
                        if inv1 != inv2:
                            print(
                                f"\tINV: {letter_sets(parsed_guesses.invalid)}, {inv1=}, {i=}; {inv2=}, {j=}"
                            )
                            break
        for invalid_kind in ("set", "absent", "exclude"):
            wg2 = WordleGuessesLegacy.parse(gr.guess_scores, invalid_kind)
            eligible2 = wg2.find_eligible(vocabulary)
            if eligible != eligible2:
                print(
                    f">> {invalid_kind + ':':<8} {wg2} "
                    f"-> {choices(gr.answer, eligible2) or []}"
                )
    return failures


def main() -> int:
    namespace = parse_args()
    failures = check_scores(namespace.first_game)
    if failures:
        print(f"{failures=}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
