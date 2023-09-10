#!/usr/bin/env python3

"""Wordle Finder"""

import argparse
import logging
import string

from collections import defaultdict
from dataclasses import dataclass
from typing import cast

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
    namespace = parser.parse_args()
    set_verbosity(namespace)
    namespace.guess_scores = [GuessScore.make(gs) for gs in namespace.guess_scores]
    return namespace


@dataclass
class WordleGuesses:
    mask: list[str | None]  # Exact match for position (Green/Correct)
    valid: set[str]  # Green/Correct or Yellow/Present
    invalid: list[set[str]]  # Black/Absent
    wrong_spot: list[set[str]]  # Wrong spot (Yellow/Present)
    guess_scores: list[GuessScore]

    def string_parts(self) -> dict[str, str]:
        unused = (
            set(string.ascii_uppercase)
            - self.valid
            - cast(set[str], set.union(*self.invalid))
        )
        guess_scores = ", ".join(f"{gs}|{gs.emojis()}" for gs in self.guess_scores)
        return dict(
            mask=dash_mask(self.mask),
            valid=letter_set(self.valid),
            invalid=letter_sets(self.invalid),
            wrong_spot=letter_sets(self.wrong_spot),
            unused=letter_set(unused),
            guess_scores=[guess_scores],
        )

    def __str__(self) -> str:
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
        parts = []
        remaining: dict[str, int] = defaultdict(int)

        for i, (a, g) in enumerate(zip(actual, guess)):
            assert "A" <= a <= "Z", "ACTUAL should be uppercase"
            assert "A" <= g <= "Z", "GUESS should be uppercase"
            if a == g:
                # Green: correct: exact match at position `i` => uppercase
                parts.append(a)
            else:
                remaining[a] += 1
                parts.append("?")

        for i, g in enumerate(guess):
            if parts[i] == "?":
                if remaining.get(g, 0) > 0:
                    # Yellow: letter present elsewhere => lowercase
                    remaining[g] -= 1
                    parts[i] = g.lower()
                else:
                    # Black: letter completely absent
                    parts[i] = "."

        return "".join(parts)

    @classmethod
    def parse(cls, guess_scores: list[GuessScore]) -> "WordleGuesses":
        mask: list[str | None] = [None for _ in range(WORDLE_LEN)]
        valid: set[str] = set()
        invalid: list[set[str]] = [set() for _ in range(WORDLE_LEN)]
        wrong_spot: list[set[str]] = [set() for _ in range(WORDLE_LEN)]

        for gs in guess_scores:
            # First pass for correct and present
            for i, (g, t) in enumerate(zip(gs.guess, gs.tiles)):
                if t is TileState.CORRECT:
                    mask[i] = g
                    valid.add(g)
                    invalid[i] = set()
                elif t is TileState.PRESENT:
                    valid.add(g)
                    wrong_spot[i].add(g)

            # Second pass for absent letters
            for i, (g, t) in enumerate(zip(gs.guess, gs.tiles)):
                if t is TileState.ABSENT:
                    for j in range(WORDLE_LEN):
                        # If we don't have a correct letter for this other position,
                        # treat `g` as invalid. This handles repeated letters.
                        if mask[j] is None:
                            invalid[j].add(g)

        parsed_guesses = cls(mask, valid, invalid, wrong_spot, guess_scores)
        logging.info(parsed_guesses)
        return parsed_guesses

    def is_eligible(self, word: str) -> tuple[bool, list[str]]:
        reasons = []
        if missing := self.valid - ({c for c in word} & self.valid):
            # Did not have the full set of green+yellow letters known to be valid
            reasons.append(f"!Valid: needs {letter_set(missing)}")

        invalid = [(c if c in inv else None) for c, inv in zip(word, self.invalid)]
        if any(invalid):
            # Invalid (black) letters present at specific positions
            reasons.append(f"Invalid: has {dash_mask(invalid)}")

        mask = [(m if c != m else None) for c, m in zip(word, self.mask)]
        if any(mask):
            # Couldn't find all the green/correct letters
            reasons.append(f"!Mask: needs {dash_mask(mask)}")

        wrong = [(c if c in ws else None) for c, ws in zip(word, self.wrong_spot)]
        if any(wrong):
            # Found some yellow letters: valid letters in wrong position
            reasons.append(f"WrongSpot: has {dash_mask(wrong)}")

        return len(reasons) == 0, reasons

    def find_eligible(self, vocabulary: list[str]) -> list[str]:
        results = []
        for w in vocabulary:
            eligible, reasons = self.is_eligible(w)
            if eligible:
                results.append(w)
            else:
                logging.debug(f"{w}: {'; '.join(reasons)}")
        return results


def main() -> int:
    namespace = parse_args(description="Wordle Finder")
    vocabulary = namespace.words or read_vocabulary(namespace.word_file)
    parsed_guesses = WordleGuesses.parse(namespace.guess_scores)
    choices = parsed_guesses.find_eligible(vocabulary)
    print("\n".join(choices))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
