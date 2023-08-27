#!/usr/bin/env python3

"""Wordle Finder"""

import argparse
import os


from common import debug, make_argparser, read_vocabulary, set_verbosity, trace, CURR_DIR, WORDLE_LEN
from wordle import WordleGuesses


def parse_args(description: str) -> argparse.Namespace:
    parser = make_argparser(description)
    parser.set_defaults(
        style_file=os.path.join(CURR_DIR, "wordle.css"),
    )
    # TODO: add more arguments
    namespace = parser.parse_args()
    set_verbosity(namespace)
    return namespace


def render_html_table(guess_scores: list[str]) -> str:
    rows = []
    for gs in guess_scores:
        guess, score = gs.split("=")
        row = []
        for cs, g in zip(WordleGuesses.cell_states(score), guess):
            css_class = ('"' + str(cs).rsplit(".")[-1].lower() + '" ')[:9]
            row.append(f"<td class={css_class}>{g}</td>") 
        rows.append("<tr>" + " ".join(row) + "</tr>")
    return "<table class='wordle'>\n  " + "\n  ".join(rows) + "\n</table>"


def render_html(guess_scores: list[str], style_file: str) -> str:
    return f"""\
<html>
<head>
    <link rel="stylesheet" href="{os.path.basename(style_file)}">
</head>
<body>
{render_html_table(guess_scores)}
</body>
</html>
"""


def main() -> int:
    namespace = parse_args(description="Render Wordle Game as HTML")
    print(render_html(namespace.guess_scores, namespace.style_file))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())