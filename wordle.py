#!/usr/bin/env python3

"""Wordle Finder"""

from __future__ import annotations

import argparse
import logging
import string
from collections import Counter
from dataclasses import dataclass
from typing import Any

from common import (
    WORDLE_LEN,
    GuessScore,
    TileState,
    argparse_wordlist,
    dash_mask,
    letter_set,
    letter_sets,
    make_argparser,
    read_vocabulary,
    set_verbosity,
)


def parse_args(description: str) -> argparse.Namespace:
    parser = make_argparser(description)
    argparse_wordlist(parser)
    parser.add_argument(
        "--explain",
        "-x",
        type=int,
        default=0,
        const=100,
        nargs="?",
        metavar="NUM-WORDS",
        help="Explain why words were rejected. Limit: %(const)s",
    )
    namespace = parser.parse_args()
    set_verbosity(namespace)
    namespace.vocabulary = namespace.words or read_vocabulary(namespace.word_file)
    if 0 < namespace.explain < len(namespace.vocabulary):
        parser.error(
            f"Vocabulary too large ({len(namespace.vocabulary)} words): "
            "use --words or specify "
            f"a higher limit with --explain (currently {namespace.explain})"
        )
    namespace.guess_scores = [GuessScore.make(gs) for gs in namespace.guess_scores]
    return namespace


@dataclass
class WordleGuesses:
    mask: list[str | None]  # Exact match for position (Green/Correct)
    valid: set[str]  # Green/Correct or Yellow/Present
    invalid: set[str]  # Black/Absent
    wrong_spot: list[set[str]]  # Wrong spot (Yellow/Present)
    guess_scores: list[GuessScore]

    def string_parts(self) -> dict[str, Any]:
        unused = letter_set(set(string.ascii_uppercase) - self.valid - self.invalid)
        guess_scores = ", ".join(f"{gs}|{gs.emojis()}" for gs in self.guess_scores)
        return dict(
            mask=dash_mask(self.mask),
            valid=letter_set(self.valid),
            invalid=letter_set(self.invalid),
            wrong_spot=letter_sets(self.wrong_spot),
            unused=unused,
            guess_scores=[guess_scores],
        )

    def __repr__(self) -> str:
        parts = ", ".join(
            f"{k}={v}"
            for k, v in self.string_parts().items()
            if k not in {"guess_scores"}
        )
        return f"{self.__class__.__name__}({parts})"

    @classmethod
    def score(cls, actual: str, guess: str) -> str:
        assert len(actual) == WORDLE_LEN
        assert len(guess) == WORDLE_LEN
        parts: list[str] = []
        remaining: Counter[str] = Counter()

        for a, g in zip(actual, guess):
            assert "A" <= a <= "Z", "ACTUAL should be uppercase"
            assert "A" <= g <= "Z", "GUESS should be uppercase"
            if a == g:
                # Green: correct: exact match at this position => uppercase
                parts.append(a)
            else:
                remaining += Counter(a)
                parts.append("?")

        for i, g in enumerate(guess):
            if parts[i] == "?":
                if remaining.get(g, 0) > 0:
                    # Yellow: letter present elsewhere => lowercase
                    remaining -= Counter(g)
                    parts[i] = g.lower()
                else:
                    # Black: letter completely absent
                    parts[i] = "."

        return "".join(parts)

    @classmethod
    def parse(cls, guess_scores: list[GuessScore]) -> "WordleGuesses":
        mask: list[str | None] = [None for _ in range(WORDLE_LEN)]
        valid: set[str] = set()
        invalid: set[str] = set()
        wrong_spot: list[set[str]] = [set() for _ in range(WORDLE_LEN)]

        for gs in guess_scores:
            # First pass for correct and present
            for i, (t, g) in enumerate(zip(gs.tiles, gs.guess)):
                if t is TileState.CORRECT:
                    mask[i] = g
                    valid.add(g)
                elif t is TileState.PRESENT:
                    wrong_spot[i].add(g)
                    valid.add(g)

            # Second pass for absent letters
            for i, (t, g) in enumerate(zip(gs.tiles, gs.guess)):
                if t is TileState.ABSENT:
                    if g in valid:
                        # There are more instances of `g` in `gs.guess`
                        # than in the answer
                        wrong_spot[i].add(g)
                    else:
                        invalid.add(g)

        parsed_guesses = cls(mask, valid, invalid, wrong_spot, guess_scores)
        logging.info(parsed_guesses)
        parsed_guesses.optimize()
        return parsed_guesses

    def is_eligible(self, word: str) -> bool:
        letters = {c for c in word}
        if letters & self.valid != self.valid:
            # Did not have the full set of green+yellow letters known to be valid
            logging.debug("!Valid: %s", word)
            return False
        elif any(m is not None and c != m for c, m in zip(word, self.mask)):
            # Couldn't find all the green/correct letters
            logging.debug("!Mask: %s", word)
            return False
        elif letters & self.invalid:
            # Invalid (black) letters present
            logging.debug("Invalid: %s", word)
            return False
        elif any(c in ws for c, ws in zip(word, self.wrong_spot)):
            # Found some yellow letters: valid letters in wrong position
            logging.debug("WrongSpot: %s", word)
            return False
        else:
            # Potentially valid
            logging.info("Got: %s", word)
            return True

    def find_eligible(self, vocabulary: list[str]) -> list[str]:
        return [w for w in vocabulary if self.is_eligible(w)]

    def is_ineligible(self, word: str) -> dict[str, str]:
        reasons = {}
        letters = {c for c in word}
        if missing := self.valid - (letters & self.valid):
            # Did not have the full set of green+yellow letters known to be valid
            reasons["Valid"] = f"missing {letter_set(missing)}"

        mask = [(m if c != m else None) for c, m in zip(word, self.mask)]
        if any(mask):
            # Couldn't find all the green/correct letters
            reasons["Mask"] = f"needs {dash_mask(mask)}"

        invalid = [(c if c in self.invalid else None) for c in word]
        if any(invalid):
            # Invalid (black) letters present at specific positions
            reasons["Invalid"] = f"has {dash_mask(invalid)}"

        wrong = [(c if c in ws else None) for c, ws in zip(word, self.wrong_spot)]
        if any(wrong):
            # Found some yellow letters: valid letters in wrong position
            reasons["WrongSpot"] = f"has {dash_mask(wrong)}"

        return reasons

    def find_explanations(self, vocabulary: list[str]) -> list[tuple[str, str | None]]:
        explanations = []
        for w in vocabulary:
            reasons = self.is_ineligible(w)
            why = None
            if reasons:
                why = "; ".join(f"{k}: {v}" for k, v in self.is_ineligible(w).items())
            explanations.append((w, why))
        return explanations

    def optimize(self) -> list[str | None]:
        """Use PRESENT tiles to improve `mask`."""
        mask1: list[str | None] = self.mask
        mask2: list[str | None] = [None] * WORDLE_LEN
        # Compute `valid`, a multi-set of the correct and present letters in all guesses
        valid: Counter[str] = Counter()
        for gs in self.guess_scores:
            valid |= Counter(
                g for g, t in zip(gs.guess, gs.tiles) if t is not TileState.ABSENT
            )
        correct = Counter(c for c in mask1 if c is not None)
        # Compute `present`, a multi-set of the valid letters
        # whose correct position is not yet known; i.e., PRESENT in any row.
        present = valid - correct
        logging.debug(f"{valid=} {correct=} {present=}")

        def available(c, i):
            "Can `c` be placed in slot `i` of `mask2`?"
            return mask1[i] is None and mask2[i] is None and c not in self.wrong_spot[i]

        while present:
            for c in present:
                positions = [i for i in range(WORDLE_LEN) if available(c, i)]
                # Is there only one position where `c` can be placed?
                if len(positions) == 1:
                    i = positions[0]
                    mask2[i] = c
                    present -= Counter(c)
                    logging.debug(f"{i+1} -> {c}")
                    break
            else:
                # We reach this for-else only if there was no `break` in the for-loop;
                # i.e., no one-element `positions` was found in `present`.
                # We must abandon the outer loop, even though `present` is not empty.
                break

        logging.debug(f"{present=} {mask2=}")

        self.mask = [m1 or m2 for m1, m2 in zip(mask1, mask2)]
        logging.info(
            f"\toptimize: {dash_mask(mask1)} | {dash_mask(mask2)}"
            f" => {dash_mask(self.mask)}"
        )
        return mask2


def main() -> int:
    namespace = parse_args(description="Wordle Finder")
    wg = WordleGuesses.parse(namespace.guess_scores)
    if namespace.explain:
        print(wg)
        print("\tguess_scores:", wg.string_parts()["guess_scores"])
        explanations = wg.find_explanations(namespace.vocabulary)
        for word, why in explanations:
            why = "❌ " + why if why else "✅ Eligible"
            print(f"{word}\t{why}")
    else:
        choices = wg.find_eligible(namespace.vocabulary)
        print("\n".join(choices or ["--None--"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
