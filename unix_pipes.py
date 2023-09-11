#!/usr/bin/env python3

"""Unix Pipes Generator"""

import argparse
import subprocess

from common import (
    GuessScore,
    letter_set,
    make_argparser,
    set_verbosity,
)
from wordle import WordleGuesses


def parse_args(description: str) -> argparse.Namespace:
    parser = make_argparser(description)
    namespace = parser.parse_args()
    set_verbosity(namespace)
    namespace.guess_scores = [GuessScore.make(gs) for gs in namespace.guess_scores]
    return namespace


def pipes(guess_scores: list[GuessScore]) -> str:
    wg = WordleGuesses.parse(guess_scores)
    mask = "grep '^" + "".join(m or "." for m in wg.mask) + "$'"
    valid = "awk '" + " && ".join(f"/{c}/" for c in sorted(wg.valid)) + "'"
    # TODO: control flavor of invalid handling
    invalid = "grep -v '[" + "".join(sorted(set.union(*wg.invalid))) + "]'"
    wrong_spots = "".join(
        [f"[^{letter_set(ws)}]" if ws else "." for ws in wg.wrong_spot]
    )
    wrong_spot = f"grep '^{wrong_spots}$'"
    return (
        "grep '^.....$' /usr/share/dict/words | tr 'a-z' 'A-Z' | "
        f"{mask} | {valid} | {invalid} | {wrong_spot}"
    )


def main() -> int:
    namespace = parse_args(description="Render hardcoded Unix pipes for Wordle game")
    cmd_line = pipes(namespace.guess_scores)
    print(cmd_line)
    print(subprocess.check_output(cmd_line, shell=True).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
