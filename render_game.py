#!/usr/bin/env python3

"""Wordle Finder"""

import argparse
import os

from common import (
    make_argparser,
    set_verbosity,
    CURR_DIR,
    WORDLE_LEN,
    GuessScore,
    output_file,
)


def parse_args(description: str) -> argparse.Namespace:
    parser = make_argparser(description)
    parser.set_defaults(
        style_file=os.path.join(CURR_DIR, "wordle.css"),
    )
    parser.add_argument("--emoji", "-E", action="store_true", help="Render emojis")
    parser.add_argument("--html", "-H", action="store_true", help="Render HTML")
    parser.add_argument("--output", "-o", help="Output filename")
    parser.add_argument("--game", "-g", dest="game_id", help="Number of game")
    namespace = parser.parse_args()
    set_verbosity(namespace)
    namespace.guess_scores = [GuessScore.make(gs) for gs in namespace.guess_scores]
    return namespace


def render_html_table(guess_scores: list[GuessScore]) -> str:
    def css_class(gs: GuessScore, i: int) -> str:
        return ('"' + gs.tiles[i].name.lower() + '" ')[:9]

    rows = []
    for gs in guess_scores:
        row = [
            f"<td class={css_class(gs, i)}>{gs.guess[i]}</td>"
            for i in range(WORDLE_LEN)
        ]
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
</html>\
"""


def render_emojis(guess_scores: list[GuessScore], game_id: str) -> str:
    header = f"Wordle {game_id} {len(guess_scores)}/6\n\n" if game_id else ""
    rows = [gs.emojis(" ") for gs in guess_scores]
    return header + "\n".join(rows)


def main() -> int:
    namespace = parse_args(description="Render Wordle Game as HTML or Emojis")
    if namespace.html:
        with output_file(namespace.output, ".html") as f:
            print(render_html(namespace.guess_scores, namespace.style_file), file=f)
    if namespace.emoji:
        with output_file(namespace.output, ".txt") as f:
            print(render_emojis(namespace.guess_scores, namespace.game_id), file=f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
