#!/usr/bin/env python3

import logging
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum

from common import (
    WORDLE_LEN,
    argparse_wordlist,
    make_argparser,
    read_vocabulary,
    set_verbosity,
)


def parse_args():
    parser = make_argparser("Wordle Finder")
    argparse_wordlist(parser)
    namespace = parser.parse_args()
    set_verbosity(namespace)
    return namespace


class WordleError(Exception):
    """Base exception class"""


class TileState(namedtuple("TileState", "value emoji color css_color"), Enum):
    CORRECT = 1, "\U0001F7E9", "Green", "#6aaa64"
    PRESENT = 2, "\U0001F7E8", "Yellow", "#c9b458"
    ABSENT = 3, "\U00002B1B", "Black", "#838184"


@dataclass
class GuessScore:
    guess: str
    score: str
    tiles: list[TileState]

    @classmethod
    def make(cls, guess_score: str) -> "GuessScore":
        if guess_score.count("=") != 1:
            raise WordleError(f"Expected one '=' in {guess_score!r}")
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
    mask: list[str | None]  # Exact match for position (Green/Correct)
    valid: set[str]  # Green/Correct or Yellow/Present
    invalid: set[str]  # Black/Absent
    wrong_spot: list[set[str]]  # Wrong spot (Yellow/Present)
    guess_scores: list[GuessScore]

    @classmethod
    def parse(cls, guess_scores: list[GuessScore]) -> "WordleGuesses":
        mask: list[str | None] = [None] * WORDLE_LEN
        valid: set[str] = set()
        invalid: set[str] = set()
        wrong_spot: list[set[str]] = [set() for _ in range(WORDLE_LEN)]

        for gs in guess_scores:
            for i, (t, g) in enumerate(zip(gs.tiles, gs.guess)):
                if t is TileState.CORRECT:
                    mask[i] = g
                    valid.add(g)
                elif t is TileState.PRESENT:
                    wrong_spot[i].add(g)
                    valid.add(g)
                elif t is TileState.ABSENT:
                    invalid.add(g)

        return cls(mask, valid, invalid, wrong_spot, guess_scores)

    def is_eligible(self, word: str) -> bool:
        letters = {c for c in word}
        if letters & self.valid != self.valid:
            # Did not have the full set of green+yellow letters known to be valid
            logging.debug("!Valid: %s", word)
            return False
        elif letters & self.invalid:
            # Invalid (black) letters are in the word
            logging.debug("Invalid: %s", word)
            return False
        elif any(m is not None and c != m for c, m in zip(word, self.mask)):
            # Couldn't find all the green/correct letters
            logging.debug("!Mask: %s", word)
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


def main() -> int:
    namespace = parse_args()
    vocabulary = namespace.words or read_vocabulary(namespace.word_file)
    guess_scores = [GuessScore.make(gs) for gs in namespace.guess_scores]
    parsed_guesses = WordleGuesses.parse(guess_scores)
    choices = parsed_guesses.find_eligible(vocabulary)
    print("\n".join(choices or ["--None--"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
