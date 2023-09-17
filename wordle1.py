#!/usr/bin/env python3

import logging

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


def parse_guesses(guess_scores):
    invalid = set()  # Black/Absent
    valid = set()  # Green/Correct or Yellow/Present
    mask = [None] * WORDLE_LEN  # Exact match for pos (Green/Correct)
    wrong_spot = [set() for _ in range(WORDLE_LEN)]  # Wrong spot (Yellow/Present)
    for gs in guess_scores:
        assert gs.count("=") == 1
        guess, score = gs.split("=")
        assert len(guess) == WORDLE_LEN
        assert len(score) == WORDLE_LEN
        for i, (g, s) in enumerate(zip(guess, score)):
            assert "A" <= g <= "Z", "GUESS should be uppercase"
            if "A" <= s <= "Z":
                assert g == s
                valid.add(g)
                mask[i] = g
            elif "a" <= s <= "z":
                assert g == s.upper()
                valid.add(g)
                wrong_spot[i].add(g)
            elif s == ".":
                invalid.add(g)
            else:
                raise ValueError(f"Unexpected {s} for {g}")
    return (invalid, valid, mask, wrong_spot)


def is_eligible(word, invalid, valid, mask, wrong_spot):
    letters = {c for c in word}
    if letters & valid != valid:
        logging.debug(f"!Valid: {word}")
        return False
    elif letters & invalid:
        logging.debug(f"Invalid: {word}")
        return False
    elif any(m is not None and c != m for c, m in zip(word, mask)):
        logging.debug(f"!Mask: {word}")
        return False
    elif any(c in ws for c, ws in zip(word, wrong_spot)):
        logging.debug(f"WrongSpot: {word}")
        return False
    else:
        logging.debug(f"Got: {word}")
        return True


def main():
    namespace = parse_args()
    vocabulary = namespace.words or read_vocabulary(namespace.word_file)
    invalid, valid, mask, wrong_spot = parse_guesses(namespace.guess_scores)
    print(f"{invalid=}")
    print(f"{valid=}")
    print(f"{mask=}")
    print(f"{wrong_spot=}")
    choices = [
        w for w in vocabulary if is_eligible(w, invalid, valid, mask, wrong_spot)
    ]
    print("\n".join(choices or ["--None--"]))


if __name__ == "__main__":
    main()
