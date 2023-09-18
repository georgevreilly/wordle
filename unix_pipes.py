#!/usr/bin/env python3

"""Unix Pipes Generator"""

import argparse
import subprocess

from common import (
    GuessScore,
    WordleError,
    argparse_wordlist,
    letter_set,
    make_argparser,
    set_verbosity,
)
from wordle import WordleGuesses


def parse_args(description: str) -> argparse.Namespace:
    parser = make_argparser(description)
    argparse_wordlist(parser)
    parser.set_defaults(
        invalid="tiles",
    )
    invalid_group = parser.add_mutually_exclusive_group()
    invalid_group.add_argument(
        "--invalid-set",
        "-S",
        dest="invalid",
        const="set",
        action="store_const",
        help="Original: combined set of invalid letters",
    )
    invalid_group.add_argument(
        "--exclude-valid",
        "-X",
        dest="invalid",
        const="exclude",
        action="store_const",
        help="Invalid, excluding valid",
    )
    invalid_group.add_argument(
        "--invalid-tiles",
        "-T",
        dest="invalid",
        const="tiles",
        action="store_const",
        help="Per-tile invalid set",
    )
    namespace = parser.parse_args()
    set_verbosity(namespace)
    namespace.guess_scores = [GuessScore.make(gs) for gs in namespace.guess_scores]
    namespace.wordle_guesses = WordleGuesses.parse(namespace.guess_scores)
    return namespace


def make_invalid(wg: WordleGuesses, invalid_kind: str) -> str | None:
    if not any(wg.invalid):
        return None
    if invalid_kind == "tiles":
        return (
            "grep '^"
            + "".join(["." if m else f"[^{letter_set(wg.invalid)}]" for m in wg.mask])
            + "$'"
        )
    else:
        # Reproduce the older behaviors of invalid
        if invalid_kind == "set":
            # a simple combined set
            combined = wg.invalid
        elif invalid_kind == "exclude":
            # exclude valid from the combined set
            combined = wg.invalid - wg.valid
        else:
            raise WordleError(f"Invalid kind: {invalid_kind}")
        return "grep -v '[" + letter_set(combined) + "]'"


def parts(wg: WordleGuesses, invalid_kind: str) -> dict[str, str | None]:
    mask = valid = wrong_spot = None
    if any(wg.mask):
        mask = "grep '^" + "".join(m or "." for m in wg.mask) + "$'"
    if wg.valid:
        valid = "awk '" + " && ".join(f"/{c}/" for c in sorted(wg.valid)) + "'"
    invalid = make_invalid(wg, invalid_kind)
    if any(wg.wrong_spot):
        wrong_spot = (
            "grep '^"
            + "".join([f"[^{letter_set(ws)}]" if ws else "." for ws in wg.wrong_spot])
            + "$'"
        )
    return dict(mask=mask, valid=valid, invalid=invalid, wrong_spot=wrong_spot)


def pipes(wg: WordleGuesses, invalid_kind: str, word_file: str) -> str:
    return " |\n\t".join(
        [f"grep '^.....$' {word_file}", "tr 'a-z' 'A-Z'"]
        + [v for v in parts(wg, invalid_kind).values() if v is not None]
    )


def main() -> int:
    namespace = parse_args(description="Render hardcoded Unix pipes for Wordle game")
    cmd_line = pipes(namespace.wordle_guesses, namespace.invalid, namespace.word_file)
    print(cmd_line)
    print(subprocess.run(cmd_line, stdout=subprocess.PIPE, shell=True).stdout.decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
