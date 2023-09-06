#!/usr/bin/env python3

"""Wordle Finder"""

import argparse
import string

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from common import (
    debug, make_argparser, read_vocabulary, set_verbosity, trace, WORDLE_LEN,
    TileState, GuessScore,
)


def parse_args(description: str) -> argparse.Namespace:
    parser = make_argparser(description)
    namespace = parser.parse_args()
    set_verbosity(namespace)
    return namespace


def letter_set(s: set[str]) -> str:
    return "".join(sorted(s))


def letter_sets(ls: list[set[str]]) -> str:
    return "[" + ",".join(letter_set(e) or "-" for e in ls) + "]"


@dataclass
class WordleGuesses:
    mask: list[Optional[str]]   # Exact match for position (Green/Correct)
    valid: set[str]             # Green/Correct or Yellow/Present
    invalid: list[set[str]]     # Black/Absent
    wrong_spot: list[set[str]]  # Wrong spot (Yellow/Present)
    guess_scores: list[GuessScore]

    def __str__(self) -> str:
        all_absent: set[str] = set.union(*self.invalid)
        unused = set(string.ascii_uppercase) - self.valid - all_absent
        guess_scores = ", ".join(f"{gs}|{gs.emojis()}" for gs in self.guess_scores)
        parts = ", ".join([
            f"mask={''.join(m or '-' for m in self.mask)}",
            f"valid={letter_set(self.valid)}",
            f"invalid={letter_sets(self.invalid)}",
            f"wrong_spot={letter_sets(self.wrong_spot)}",
            f"unused={letter_set(unused)}",
            f"guess_scores=[{guess_scores}]",
        ])
        return (f"WordleGuesses({parts})")

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
    def parse(cls, guess_scores: list[GuessScore]) -> 'WordleGuesses':
        mask: list[Optional[str]] = [None] * WORDLE_LEN
        valid: set[str] = set()
        invalid: list[set[str]] = [set() for _ in range(WORDLE_LEN)]
        wrong_spot: list[set[str]] = [set() for _ in range(WORDLE_LEN)]

        for gs in guess_scores:
            # First pass for correct and present
            for i in range(WORDLE_LEN):
                if gs.tiles[i] is TileState.CORRECT:
                    mask[i] = gs.guess[i]
                    valid.add(gs.guess[i])
                    invalid[i] = set()
                elif gs.tiles[i] is TileState.PRESENT:
                    valid.add(gs.guess[i])
                    wrong_spot[i].add(gs.guess[i])

            # Second pass for absent letters
            for i in range(WORDLE_LEN):
                if gs.tiles[i] is TileState.ABSENT:
                    for j in range(WORDLE_LEN):
                        # If we don't have a correct letter for this other position,
                        # treat `g` as invalid. This handles repeated letters.
                        if mask[j] is None:
                            invalid[j].add(gs.guess[i])

        parsed_guesses = cls(mask, valid, invalid, wrong_spot, guess_scores)
        debug(parsed_guesses)
        return parsed_guesses

    def is_eligible(self, word: str) -> bool:
        letters = {c for c in word}
        if letters & self.valid != self.valid:
            # Did not have the full set of green+yellow letters known to be valid
            trace(f"!Valid: {word}")
            return False
        elif any(c in inv for c, inv in zip(word, self.invalid)):
            # Invalid (black) letters present at specific positions
            trace(f"Invalid: {word}")
            return False
        elif any(m is not None and c != m for c, m in zip(word, self.mask)):
            # Couldn't find all the green/correct letters
            trace(f"!Mask: {word}")
            return False
        elif any(c in ws for c, ws in zip(word, self.wrong_spot)):
            # Found some yellow letters: valid letters in wrong position
            trace(f"WrongSpot: {word}")
            return False
        else:
            # Potentially valid
            debug(f"Got: {word}")
            return True

    def find_eligible(self, vocabulary: list[str]) -> list[str]:
        return [w for w in vocabulary if self.is_eligible(w)]


def main() -> int:
    namespace = parse_args(description="Wordle Finder")
    guess_scores = [GuessScore.make(gs) for gs in namespace.guess_scores]
    vocabulary = namespace.words or read_vocabulary(namespace.word_file)
    parsed_guesses = WordleGuesses.parse(guess_scores)
    choices = parsed_guesses.find_eligible(vocabulary)
    print("\n".join(choices))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
