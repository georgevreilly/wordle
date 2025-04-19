#!/usr/bin/env python3

"""Unix Pipes Generator"""

from __future__ import annotations

import argparse
import os
import subprocess

from common import (
    WORDLE_LEN,
    GuessScore,
    TileState,
    argparse_wordlist,
    letter_set,
    make_argparser,
    set_verbosity,
)
from wordle import WordleGuesses


def parse_args(description: str) -> argparse.Namespace:
    parser = make_argparser(description)
    argparse_wordlist(parser)
    namespace = parser.parse_args()
    set_verbosity(namespace)
    namespace.guess_scores = [GuessScore.make(gs) for gs in namespace.guess_scores]
    namespace.wordle_guesses = WordleGuesses.parse(namespace.guess_scores, optimize=False)
    return namespace


def parts(wg: WordleGuesses) -> dict[str, str | None]:
    mask = valid = invalid = wrong_spot = None
    if wg.valid:
        valid = "awk '" + " && ".join(f"/{c}/" for c in sorted(wg.valid)) + "'"
    if any(wg.mask):
        mask = "grep '^" + "".join(m or "." for m in wg.mask) + "$'"
    if wg.invalid:
        ordered = []
        for gs in wg.guess_scores:
            for i in range(WORDLE_LEN):
                if gs.tiles[i] is TileState.ABSENT:
                    if gs.guess[i] not in ordered and gs.guess[i] in wg.invalid:
                        ordered.append(gs.guess[i])
        invalid = "grep -v '[" + "".join(ordered) + "]'"
    if any(wg.wrong_spot):
        wrong_spot = (
            "grep '^"
            + "".join([f"[^{letter_set(ws)}]" if ws else "." for ws in wg.wrong_spot])
            + "$'"
        )
    return dict(mask=mask, valid=valid, invalid=invalid, wrong_spot=wrong_spot)


def pipes(wg: WordleGuesses, word_file: str) -> str:
    return " |\n\t".join(
        ["env LC_ALL=C \\\n" + "egrep '^[a-z]{5}$' " + word_file, "tr 'a-z' 'A-Z'"]
        + [v for v in parts(wg).values() if v is not None]
    )


def run_pipe(cmd_line: str) -> str:
    return subprocess.run(
        cmd_line,
        stdout=subprocess.PIPE,
        shell=True,
        # env=os.environ | dict(LC_ALL="C")
        ).stdout.decode()


def main() -> int:
    namespace = parse_args(description="Render hardcoded Unix pipes for Wordle game")
    cmd_line = pipes(namespace.wordle_guesses, namespace.word_file)
    print(cmd_line)
    print(run_pipe(cmd_line))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
