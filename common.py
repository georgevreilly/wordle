import argparse
import os
import re
import string
import sys

from collections import namedtuple
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Optional


DICT_FILE = "/usr/share/dict/words"
CURR_DIR = os.path.abspath(os.path.dirname(__file__))
WORD_FILE = os.path.join(CURR_DIR, "wordle.txt")
GAMES_FILE = os.path.join(os.path.dirname(__file__), "games.md")
WORDLE_LEN = 5
_VERBOSITY = 0


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
class GameResult:
    game_id: int
    answer: str
    verb: str
    guess_scores: list[GuessScore]

    GAME_RE: ClassVar[re.Pattern] = re.compile(
        r"""^\* (?P<game>[0-9]+): `(?P<guess_scores>[^`]+)`(?P<verb>[^`]+)`(?P<answer>[A-Z]+)`$""")

    @classmethod
    def parse_game_results(cls, filename: str) -> 'list[GameResult]':
        results: list[GameResult] = []
        with open(filename) as f:
            for line in f.read().splitlines():
                if line.startswith("* ") and line.count("`") == 4:
                    m = cls.GAME_RE.match(line)
                    assert m is not None
                    game_id = int(m.group("game"))
                    answer = m.group("answer")
                    verb = m.group("verb").strip().strip('*')
                    assert verb in {"yields", "includes"}
                    guess_scores = [GuessScore.make(gs) for gs in m.group("guess_scores").split()]
                    results.append(GameResult(game_id, answer, verb, guess_scores))
        return results


def make_argparser(description: str, word_file = WORD_FILE) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description)
    parser.set_defaults(
        word_file=word_file,
        verbose=0,
    )
    words_group = parser.add_mutually_exclusive_group()
    words_group.add_argument(
        "--word-file", "-f", metavar="FILENAME",
        help="Word file. Default: %(default)r")
    words_group.add_argument(
        "--word", "-w", action="append", dest="words", metavar="WORD",
        help="Word(s) to check")
    parser.add_argument(
        "--verbose", "-v", action="count", help="Show all the steps")
    parser.add_argument(
        "guess_scores",
        nargs="+",
        metavar="GUESS=score",
        help="Examples: 'ARISE=.r.se' 'ROUTE=R.u.e' 'RULES=Ru.eS'",
    )
    return parser


def set_verbosity(namespace: argparse.Namespace) -> argparse.Namespace:
    global _VERBOSITY
    _VERBOSITY = namespace.verbose
    return namespace


def debug(s):
    if _VERBOSITY != 0:
        print(s)


def trace(s):
    if _VERBOSITY >= 2:
        print(s)


def read_vocabulary(word_file: str = WORD_FILE) -> list[str]:
    with open(word_file) as f:
        words = []
        for w in f.read().splitlines():
            w = w.upper().strip()
            if len(w) == WORDLE_LEN:
                assert all(c in string.ascii_uppercase for c in w)
                words.append(w)
        return words


def letter_set(s: set[str]) -> str:
    return "".join(sorted(s))


def letter_sets(ls: list[set[str]]) -> str:
    return "[" + ",".join(letter_set(e) or "-" for e in ls) + "]"


def dash_mask(mask: list[Optional[str]]):
    return "".join(m or "-" for m in mask)


@contextmanager
def output_file(output: str | None, extension: str):
    if not output or output == "-":
        yield sys.stdout
    else:
        filename = os.path.splitext(output)[0] + extension
        f = open(filename, "w")
        try:
            yield f
        finally:
            f.close()
