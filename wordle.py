#!/usr/bin/env python3

"""Wordle Finder"""

import argparse

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional


WORD_FILE = "wordle.txt"
WORDLE_LEN = 5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wordle Finder")
    parser.set_defaults(
        # word_file="/usr/share/dict/words",
        word_file=WORD_FILE,
        len=WORDLE_LEN,
        verbose=0,
    )
    parser.add_argument(
        "--verbose", "-v", action="count", help="Show all the steps")
    parser.add_argument(
        "guess_scores",
        nargs="+",
        metavar="GUESS=score",
        help="Examples: 'ARISE=.r.se' 'ROUTE=R.u.e' 'RULES=Ru.eS'",
    )
    return parser.parse_args()


def debug(s):
    pass
#   if namespace.verbose != 0: print(s)


def trace(s):
    pass
#   if namespace.verbose >= 2: print(s)


def read_vocabulary(word_file: str = WORD_FILE, word_len: int = WORDLE_LEN) -> list[str]:
    with open(word_file) as f:
        return [w.upper() for w in f.read().splitlines() if len(w) == word_len]


@dataclass
class WordleGuesses:
    valid: set[str]             # Green or Yellow
    invalid: set[str]           # Black
    mask: list[Optional[str]]   # Exact match for position (Green)
    wrong_spot: list[set[str]]  # Wrong spot (Yellow)

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
    def parse(cls, guess_scores: list[str], word_len: int = WORDLE_LEN) -> 'WordleGuesses':
        valid: set[str] = set()
        invalid: set[str] = set()
        mask: list[Optional[str]] = [None] * word_len
        wrong_spot: list[set[str]] = [set() for _ in range(word_len)]

        for gs in guess_scores:
            guess, score = gs.split("=")
            assert len(guess) == word_len
            assert len(score) == word_len
            for i, (g, s) in enumerate(zip(guess, score)):
                assert "A" <= g <= "Z", "GUESS should be uppercase"
                if "A" <= s <= "Z":
                    # Green: letter is correct at this position
                    valid.add(g)
                    mask[i] = g
                elif "a" <= s <= "z":
                    # Yellow: letter is elsewhere in the word
                    valid.add(g)
                    wrong_spot[i].add(g)
                elif s == ".":
                    # Black: letter is not in the word
                    if g not in valid:
                        invalid.add(g)
                else:
                    raise ValueError(f"Unexpected {s} for {g}")
        return cls(valid, invalid, mask, wrong_spot)

    def is_eligible(self, word: str) -> bool:
        letters = {c for c in word}
        if letters & self.valid != self.valid:
            # Did not have the full set of green+yellow letters known to be valid
            trace(f"!Valid: {word}")
            return False
        elif letters & self.invalid:
            # Invalid (black) letters present
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
    namespace = parse_args()
    vocabulary = read_vocabulary(namespace.word_file, namespace.len)
    parsed_guesses = WordleGuesses.parse(namespace.guess_scores, namespace.len)
    choices = parsed_guesses.find_eligible(vocabulary)
    print("\n".join(choices))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
