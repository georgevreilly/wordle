#!/usr/bin/env python3

import argparse
import os
import string

from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from typing import Optional


DICT_FILE = "/usr/share/dict/words"
CURR_DIR = os.path.abspath(os.path.dirname(__file__))
WORD_FILE = os.path.join(CURR_DIR, "wordle.txt")
GAMES_FILE = os.path.join(os.path.dirname(__file__), "games.md")
WORDLE_LEN = 5
_VERBOSITY = 0


def debug(s):
    if _VERBOSITY != 0:
        print(s)


def trace(s):
    if _VERBOSITY >= 2:
        print(s)


def parse_args():
    parser = argparse.ArgumentParser(description="Wordle Finder")
    parser.set_defaults(
        # word_file="/usr/share/dict/words",
        word_file="wordle.txt",
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
    words_group = parser.add_mutually_exclusive_group()
    words_group.add_argument(
        "--word-file", "-f", metavar="FILENAME",
        help="Word file. Default: %(default)r")
    words_group.add_argument(
        "--word", "-w", action="append", dest="words", metavar="WORD",
        help="Word(s) to check")
    namespace = parser.parse_args()
    global _VERBOSITY
    _VERBOSITY = namespace.verbose
    return namespace


class WordleError(Exception):
    """Base exception class"""


class TileState(namedtuple("TileState", "value emoji color css_color"), Enum):
    CORRECT = 1, "\U0001F7E9", "Green",  "#6aaa64"
    PRESENT = 2, "\U0001F7E8", "Yellow", "#c9b458"
    ABSENT  = 3, "\U00002B1B", "Black",  "#838184"


@dataclass
class GuessScore:
    guess: str
    score: str
    tiles: list[TileState]

    @classmethod
    def make(cls, guess_score: str) -> 'GuessScore':
        guess, score = guess_score.split("=")
        if len(guess) != WORDLE_LEN:
            raise WordleError(f"Guess {guess!r} is not {WORDLE_LEN} characters")
        if len(score) != WORDLE_LEN:
            raise WordleError(f"Score {score!r} is not {WORDLE_LEN} characters")
        tiles = []
        for i in range(WORDLE_LEN):
            if not "A" <= guess[i] <= "Z":
                raise WordleError("Guess {guess!r} should be uppercase")
            state = cls.tile_state(score[i])
            if state is TileState.CORRECT:
                if guess[i] != score[i]:
                    raise WordleError(f"Mismatch at {i+1}: {guess}!={score}")
            elif state is TileState.PRESENT:
                if guess[i] != score[i].upper():
                    raise WordleError(f"Mismatch at {i+1}: {guess}!={score}")
            tiles.append(state)
        return cls(guess, score, tiles)

    @classmethod
    def tile_state(cls, score_tile: str) -> TileState:
        if "A" <= score_tile <= "Z":
            return TileState.CORRECT
        elif "a" <= score_tile <= "z":
            return TileState.PRESENT
        elif score_tile == ".":
            return TileState.ABSENT
        else:
            raise WordleError(f"Invalid score: {score_tile}")

    def __str__(self):
        return f"{self.guess}={self.score}"

    def emojis(self, separator=""):
        return separator.join(t.emoji for t in self.tiles)


@dataclass
class WordleGuesses:
    mask: list[Optional[str]]   # Exact match for position (Green/Correct)
    valid: set[str]             # Green/Correct or Yellow/Present
    invalid: set[str]           # Black/Absent
    wrong_spot: list[set[str]]  # Wrong spot (Yellow/Present)
    guess_scores: list[GuessScore]

    @classmethod
    def parse(cls, guess_scores: list[GuessScore]) -> 'WordleGuesses':
        mask: list[Optional[str]] = [None] * WORDLE_LEN
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
                    invalid.add(gs.guess[i])

        return cls(mask, valid, invalid, wrong_spot, guess_scores)

    def is_eligible(self, word: str) -> bool:
        letters = {c for c in word}
        if letters & self.valid != self.valid:
            # Did not have the full set of green+yellow letters known to be valid
            trace(f"!Valid: {word}")
            return False
        elif letters & self.invalid:
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
    namespace = parse_args()
    if namespace.words:
        WORDS = namespace.words
    else:
        with open(namespace.word_file) as f:
            WORDS = [w.upper().strip() for w in f
                     if len(w.strip()) == WORDLE_LEN]
    guess_scores = [GuessScore.make(gs) for gs in namespace.guess_scores]
    parsed_guesses = WordleGuesses.parse(guess_scores)
    choices = parsed_guesses.find_eligible(WORDS)
    print("\n".join(choices))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
