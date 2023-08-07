#!/usr/bin/env python3

"""Wordle Finder"""

import argparse
import os
import string

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional


WORD_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "wordle.txt"))
WORDLE_LEN = 5
VERBOSITY = 0


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
        "--word-file", "-w", help="Word file. Default: %(default)s")
    parser.add_argument(
        "guess_scores",
        nargs="+",
        metavar="GUESS=score",
        help="Examples: 'ARISE=.r.se' 'ROUTE=R.u.e' 'RULES=Ru.eS'",
    )
    namespace = parser.parse_args()
    global VERBOSITY
    VERBOSITY = namespace.verbose
    return namespace


def debug(s):
    if VERBOSITY != 0:
        print(s)


def trace(s):
    if VERBOSITY >= 2:
        print(s)


def read_vocabulary(word_file: str = WORD_FILE, word_len: int = WORDLE_LEN) -> list[str]:
    with open(word_file) as f:
        words = []
        for w in f.read().splitlines():
            w = w.upper().strip()
            if len(w) == word_len:
                assert all(c in string.ascii_uppercase for c in w)
                words.append(w)
        return words


def letter_set(s: set[str]) -> str:
    return "".join(sorted(s))


def letter_sets(ls: list[set[str]]) -> str:
    return "[" + ",".join(letter_set(e) or "-" for e in ls) + "]"


@dataclass
class WordleGuesses:
    mask: list[Optional[str]]   # Exact match for position (Green)
    valid: set[str]             # Green or Yellow
    invalid: list[set[str]]     # Black
    wrong_spot: list[set[str]]  # Wrong spot (Yellow)

    def __repr__(self) -> str:
        return ("WordleGuesses("
                f"mask={''.join(m or '-' for m in self.mask)}, "
                f"valid={letter_set(self.valid)}, "
                f"invalid={letter_sets(self.invalid)}, "
                f"wrong_spot={letter_sets(self.wrong_spot)}"
                ")")

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
    namespace = parse_args()
    vocabulary = read_vocabulary(namespace.word_file, namespace.len)
    parsed_guesses = WordleGuesses.parse(namespace.guess_scores, namespace.len)
    choices = parsed_guesses.find_eligible(vocabulary)
    print("\n".join(choices))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
