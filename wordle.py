#!/usr/bin/env python3

import argparse

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional


WORDLE_LEN = 5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wordle Finder")
    parser.set_defaults(
        # word_file="/usr/share/dict/words",
        word_file="wordle.txt",
        len=WORDLE_LEN,
        verbose=0,
    )
    parser.add_argument(
        "--verbose", "-v", action="count", help="Show all the steps")
    parser.add_argument(
        "guesses",
        nargs="+",
        metavar="WORD=guess",
        help="Examples: 'ARISE=.r.se' 'ROUTE=R.u.e' 'RULES=Ru.eS'",
    )
    return parser.parse_args()


def debug(s):
    pass
#   if namespace.verbose != 0: print(s)


def trace(s):
    pass
#   if namespace.verbose >= 2: print(s)


def read_vocabulary(word_file: str, word_len: int) -> list[str]:
    with open(word_file) as f:
        return [w.upper() for w in f.read().splitlines() if len(w) == word_len]


@dataclass
class ParsedGuesses:
    valid: set[str]             # Green or Yellow
    invalid: set[str]           # Black
    mask: list[Optional[str]]   # Exact match for position (Green)
    wrong_spot: list[set[str]]  # Wrong spot (Yellow)

    @classmethod
    def score(cls, actual: str, guess: str, word_len: int = WORDLE_LEN) -> str:
        assert len(actual) == word_len
        assert len(guess) == word_len
        result = ["?" for _ in range(word_len)]
        remaining: dict[str, int] = defaultdict(int)

        for i, (a, g) in enumerate(zip(actual, guess)):
            assert "A" <= a <= "Z", "ACTUAL should be uppercase"
            assert "A" <= g <= "Z", "GUESS should be uppercase"
            if a == g:
                # Green
                result[i] = a
            else:
                remaining[a] += 1

        for i, g in enumerate(guess):
            if result[i] == "?":
                if remaining.get(g, 0) > 0:
                    # Yellow
                    remaining[g] -= 1
                    result[i] = g.lower()
                else:
                    # Black
                    result[i] = "."

        return "".join(result)

    @classmethod
    def parse(cls, guesses: list[str], word_len: int = WORDLE_LEN) -> 'ParsedGuesses':
        valid: set[str] = set()
        invalid: set[str] = set()
        mask: list[Optional[str]] = [None] * word_len
        wrong_spot: list[set[str]] = [set() for _ in range(word_len)]

        for guess in guesses:
            word, result = guess.split("=")
            assert len(word) == word_len
            assert len(result) == word_len
            for i, (w, r) in enumerate(zip(word, result)):
                assert "A" <= w <= "Z", "WORD should be uppercase"
                if "A" <= r <= "Z":
                    valid.add(w)
                    mask[i] = w
                elif "a" <= r <= "z":
                    valid.add(w)
                    wrong_spot[i].add(w)
                elif r == ".":
                    if w not in valid:
                        invalid.add(w)
                else:
                    raise ValueError(f"Unexpected {r} for {w}")
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

    def guess(self, vocabulary: list[str]) -> list[str]:
        return [w for w in vocabulary if self.is_eligible(w)]


def main() -> int:
    namespace = parse_args()
    vocabulary = read_vocabulary(namespace.word_file, namespace.len)
    parsed_guesses = ParsedGuesses.parse(namespace.guesses, namespace.len)
    choices = parsed_guesses.guess(vocabulary)
    print("\n".join(choices))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
