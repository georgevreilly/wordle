#!/usr/bin/env python3

"""Wordle Finder"""

import argparse
import os

from common import (
    make_argparser, set_verbosity, CURR_DIR, WORDLE_LEN, GuessScore,
)


def parse_args(description: str) -> argparse.Namespace:
    parser = make_argparser(description)
    parser.set_defaults(
        style_file=os.path.join(CURR_DIR, "wordle.css"),
    )
    # TODO: add more arguments
    namespace = parser.parse_args()
    set_verbosity(namespace)
    return namespace


def render_html_table(guess_scores: list[GuessScore]) -> str:
    rows = []
    for gs in guess_scores:
        row = []
        for i in range(WORDLE_LEN):
            css_class = ('"' + gs.tiles[i].name.lower() + '" ')[:9]
            row.append(f"<td class={css_class}>{gs.guess[i]}</td>") 
        rows.append("<tr>" + " ".join(row) + "</tr>")
    return "<table class='wordle'>\n  " + "\n  ".join(rows) + "\n</table>"


def render_html(guess_scores: list[GuessScore], style_file: str) -> str:
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


def render_emojis(guess_scores: list[GuessScore], game: str) -> str:
    header = f"Wordle {game} {len(guess_scores)}/6\n\n" if game else ""
    rows = [gs.emojis(" ") for gs in guess_scores]
    return header + "\n".join(rows)


def main() -> int:
    namespace = parse_args(description="Render Wordle Game as HTML")
    guess_scores = [GuessScore.make(gs) for gs in namespace.guess_scores]
    # print(render_html(guess_scores, namespace.style_file))
    print(render_emojis(guess_scores, "775"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())