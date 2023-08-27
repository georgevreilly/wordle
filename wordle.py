#!/usr/bin/env python3

"""Wordle Finder"""

import argparse
import string

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from common import debug, make_argparser, read_vocabulary, set_verbosity, trace, WORDLE_LEN


def parse_args(description: str) -> argparse.Namespace:
    parser = make_argparser(description)
    namespace = parser.parse_args()
    set_verbosity(namespace)
    return namespace


def letter_set(s: set[str]) -> str:
    return "".join(sorted(s))


def letter_sets(ls: list[set[str]]) -> str:
    return "[" + ",".join(letter_set(e) or "-" for e in ls) + "]"


class CellState(Enum):
    CORRECT = 1  # Green
    PRESENT = 2  # Yellow
    ABSENT  = 3  # Black


@dataclass
class WordleGuesses:
    mask: list[Optional[str]]   # Exact match for position (Green/Correct)
    valid: set[str]             # Green/Correct or Yellow/Present
    invalid: list[set[str]]     # Black/Absent
    wrong_spot: list[set[str]]  # Wrong spot (Yellow/Present)

    def __str__(self) -> str:
        unused = set(string.ascii_uppercase) - self.valid - set.union(*self.invalid)
        parts = ", ".join([
            f"mask={''.join(m or '-' for m in self.mask)}",
            f"valid={letter_set(self.valid)}",
            f"invalid={letter_sets(self.invalid)}",
            f"wrong_spot={letter_sets(self.wrong_spot)}",
            f"unused={letter_set(unused)}",
        ])
        return (f"WordleGuesses({parts})")

    @classmethod
    def score(cls, actual: str, guess: str, word_len: int = WORDLE_LEN) -> str:
        assert len(actual) == word_len
        assert len(guess) == word_len
        parts = []
        remaining: dict[str, int] = defaultdict(int)

        for i, (a, g) in enumerate(zip(actual, guess)):
            assert "A" <= a <= "Z", "ACTUAL should be uppercase"
            assert "A" <= g <= "Z", "GUESS should be uppercase"
            if a == g:
                # Green: exact match at position `i` => uppercase
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
                    # Black: letter not present at all
                    parts[i] = "."

        return "".join(parts)

    @classmethod
    def cell_states(cls, score: str) -> list[CellState]:
        result = []
        for s in score:
            if "A" <= s <= "Z":
                result.append(CellState.CORRECT)
            elif "a" <= s <= "z":
                result.append(CellState.PRESENT)
            elif s == ".":
                result.append(CellState.ABSENT)
        return result

    @classmethod
    def emojis(cls, score: str, use_black: bool = True) -> str:
        state_to_emoji = {
            CellState.CORRECT: "🟩",
            CellState.PRESENT: "🟨",
            CellState.ABSENT: "⬛" if use_black else "⬜",
        }
        result = [state_to_emoji[cs] for cs in cls.cell_states(score)]
        return "".join(result)

    @classmethod
    def parse(cls, guess_scores: list[str], word_len: int = WORDLE_LEN) -> 'WordleGuesses':
        mask: list[Optional[str]] = [None] * word_len
        valid: set[str] = set()
        invalid: list[set[str]] = [set() for _ in range(word_len)]
        wrong_spot: list[set[str]] = [set() for _ in range(word_len)]

        for gs in guess_scores:
            guess, score = gs.split("=")
            assert len(guess) == word_len, f"{guess=}, {len(guess)}"
            assert len(score) == word_len, f"{score=}, {len(score)}"
            for i, (g, s) in enumerate(zip(guess, score)):
                assert "A" <= g <= "Z", "GUESS should be uppercase"
                if "A" <= s <= "Z":
                    # Green: letter is correct at this position
                    mask[i] = g
                    valid.add(g)
                    invalid[i] = set()
                elif "a" <= s <= "z":
                    # Yellow: letter is elsewhere in the word
                    valid.add(g)
                    wrong_spot[i].add(g)
                elif s != ".":
                    raise ValueError(f"Unexpected {s} for {g}")

            for i, (g, s) in enumerate(zip(guess, score)):
                if s == ".":
                    # Black: letter is not in the word
                    for j in range(word_len):
                        if mask[j] is None:
                            invalid[j].add(g)

        parsed_guesses = cls(mask, valid, invalid, wrong_spot)
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
            # Couldn't find all the green letters 
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
    vocabulary = read_vocabulary(namespace.word_file, namespace.len)
    parsed_guesses = WordleGuesses.parse(namespace.guess_scores, namespace.len)
    choices = parsed_guesses.find_eligible(vocabulary)
    print("\n".join(choices))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
