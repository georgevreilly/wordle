import argparse
import os
import string


DICT_FILE = "/usr/share/dict/words"
CURR_DIR = os.path.abspath(os.path.dirname(__file__))
WORD_FILE = os.path.join(CURR_DIR, "wordle.txt")
WORDLE_LEN = 5
_VERBOSITY = 0


def make_argparser(description: str, word_file = WORD_FILE) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description)
    parser.set_defaults(
        word_file=word_file,
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


def read_vocabulary(word_file: str = WORD_FILE, word_len: int = WORDLE_LEN) -> list[str]:
    with open(word_file) as f:
        words = []
        for w in f.read().splitlines():
            w = w.upper().strip()
            if len(w) == word_len:
                assert all(c in string.ascii_uppercase for c in w)
                words.append(w)
        return words