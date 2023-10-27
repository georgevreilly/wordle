from __future__ import annotations

import argparse
import fileinput
import logging
import os
import re
import string
import sys
from collections import namedtuple
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar

DICT_FILE = "/usr/share/dict/words"
CURR_DIR = os.path.abspath(os.path.dirname(__file__))
WORD_FILE = os.path.join(CURR_DIR, "wordle.txt")
ANSWERS_FILE = os.path.join(CURR_DIR, "answers.txt")
GAMES_FILE = os.path.join(os.path.dirname(__file__), "games.md")
WORDLE_LEN = 5


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

    def __repr__(self):
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
        r"""^\*\s(?P<game>[0-9]+):\s        # Number
            `(?P<guess_scores>[^`]+)`\s     # GUESS=SCORE ...
            \*?(?P<verb>[a-z]+)\*?\s        # "yields" or "includes"
            `(?P<answer>[A-Z]+)`$           # WORD
        """,
        re.VERBOSE,
    )

    @classmethod
    def parse_game_results(cls, filename: str) -> "list[GameResult]":
        results: list[GameResult] = []
        with open(filename) as f:
            for line in f.read().splitlines():
                if line.startswith("* ") and line.count("`") == 4:
                    m = cls.GAME_RE.match(line)
                    assert m is not None, f"{line!r}"
                    game_id = int(m.group("game"))
                    answer = m.group("answer")
                    verb = m.group("verb").strip().strip("*")
                    assert verb in {"yields", "includes"}
                    guess_scores = [
                        GuessScore.make(gs) for gs in m.group("guess_scores").split()
                    ]
                    results.append(GameResult(game_id, answer, verb, guess_scores))
        return results


def make_argparser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description)
    parser.set_defaults(
        verbose=0,
    )
    parser.add_argument("--verbose", "-v", action="count", help="Show all the steps")
    parser.add_argument(
        "guess_scores",
        nargs="+",
        metavar="GUESS=score",
        help="Examples: 'ARISE=.r.se' 'ROUTE=R.u.e' 'RULES=Ru.eS'",
    )
    return parser


def argparse_wordlist(
    parser: argparse.ArgumentParser,
    word_file: str = WORD_FILE,
    allow_individual_words=True,
) -> None:
    parser.set_defaults(
        word_file=word_file,
    )
    words_group = parser.add_mutually_exclusive_group()
    words_group.add_argument(
        "--word-file", "-f", metavar="FILENAME", help="Word file. Default: %(default)r"
    )
    words_group.add_argument(
        "--dict-words",
        "-d",
        action="store_const",
        const=DICT_FILE,
        dest="word_file",
        help=f"Use {DICT_FILE} as word file",
    )
    # Make the ~2,000 answers available,
    # but remove temptation by not documenting this option.
    words_group.add_argument(
        "--answers",
        "-A",
        action="store_const",
        const=ANSWERS_FILE,
        dest="word_file",
        help=argparse.SUPPRESS,
    )
    if allow_individual_words:
        words_group.add_argument(
            "--words", "-w", metavar="WORD", nargs="+", help="Word(s) to check"
        )


def set_verbosity(namespace: argparse.Namespace) -> argparse.Namespace:
    level = (
        logging.DEBUG
        if namespace.verbose >= 2
        else logging.INFO
        if namespace.verbose >= 1
        else logging.WARNING
    )
    logging.basicConfig(level=level, stream=sys.stdout, format="%(message)s")
    return namespace


def read_vocabulary(word_file: str = WORD_FILE) -> list[str]:
    words = set()
    for w in fileinput.input(files=(word_file,)):
        w = w.upper().strip()
        if len(w) == WORDLE_LEN:
            assert all(c in string.ascii_uppercase for c in w)
            words.add(w)
    return sorted(words)


def letter_set(s: set[str]) -> str:
    return "".join(sorted(s))


def letter_sets(ls: list[set[str]]) -> str:
    return "[" + ",".join(letter_set(e) or "-" for e in ls) + "]"


def dash_mask(mask: list[str | None]):
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


SCRABBLE_POINTS = dict(
    A=1,
    B=3,
    C=3,
    D=2,
    E=1,
    F=4,
    G=2,
    H=4,
    I=1,
    J=8,
    K=5,
    L=1,
    M=3,
    N=1,
    O=1,
    P=3,
    Q=10,
    R=1,
    S=1,
    T=1,
    U=1,
    V=4,
    W=4,
    X=8,
    Y=4,
    Z=10,
)


def scrabble_score(word: str) -> int:
    return sum(SCRABBLE_POINTS[c] for c in word)


BASE_STRING = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def to_base(number, base):
    return (
        "0"
        if not number
        else to_base(number // base, base).lstrip("0") + BASE_STRING[number % base]
    )
