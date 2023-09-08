#!/usr/bin/env python3

import argparse

from dataclasses import dataclass

from common import debug, trace, GuessScore, TileState, WORDLE_LEN


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


def parse_guesses(guess_scores):
    invalid = set()  # Black
    valid = set()  # Green or Yellow
    mask = [None] * WORDLE_LEN  # Exact match for position (Green)
    wrong_spot = [set() for _ in range(WORDLE_LEN)]  # Wrong spot (Yellow)
    for guess in guess_scores:
        word, result = guess.split("=")
        assert len(word) == WORDLE_LEN
        assert len(result) == WORDLE_LEN
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
    return (invalid, valid, mask, wrong_spot)


def is_eligible(word, invalid, valid, mask, wrong_spot):
    letters = {c for c in word}
    if letters & valid != valid:
        trace(f"!Valid: {word}")
        return False
    elif letters & invalid:
        trace(f"Invalid: {word}")
        return False
    elif any(m is not None and c != m for c, m in zip(word, mask)):
        trace(f"!Mask: {word}")
        return False
    elif any(c in ws for c, ws in zip(word, wrong_spot)):
        trace(f"WrongSpot: {word}")
        return False
    else:
        trace(f"Got: {word}")
        return True


def main():
    namespace = parse_args()
    if namespace.words:
        WORDS = namespace.words
    else:
        with open(namespace.word_file) as f:
            WORDS = [w.upper().strip() for w in f
                     if len(w.strip()) == WORDLE_LEN]
    invalid, valid, mask, wrong_spot = parse_guesses(namespace.guess_scores)
    print(f"{invalid=}")
    print(f"{valid=}")
    print(f"{mask=}")
    print(f"{wrong_spot=}")
    choices = [w for w in WORDS if is_eligible(w, invalid, valid, mask, wrong_spot)]
    print("\n".join(choices))


if __name__ == "__main__":
    main()
