#!/usr/bin/env python3

"""Wordle Finder"""

from __future__ import annotations

import argparse
import os
import string

from common import CURR_DIR, WORDLE_LEN, GuessScore, make_argparser, output_file, set_verbosity


def parse_args(description: str) -> argparse.Namespace:
    parser = make_argparser(description)
    parser.set_defaults(
        style_file=os.path.join(CURR_DIR, "wordle.css"),
    )
    parser.add_argument("--emoji", "-E", action="store_true", help="Render emojis")
    parser.add_argument("--html", "-H", action="store_true", help="Render HTML")
    parser.add_argument("--keyboard", "-K", action="store_true", help="Render Keyboard")
    parser.add_argument("--output", "-o", help="Output filename")
    parser.add_argument("--game", "-g", dest="game_id", help="Number of game")
    namespace = parser.parse_args()
    if not any([namespace.emoji, namespace.html]):
        parser.error("You must use --emoji and/or --html")
    set_verbosity(namespace)
    namespace.guess_scores = [GuessScore.make(gs) for gs in namespace.guess_scores]
    return namespace


def render_html_table(guess_scores: list[GuessScore], show_unplayed=False) -> str:
    def css_class(gs: GuessScore, i: int) -> str:
        return ('"' + gs.tiles[i].name.lower() + '" ')[:9]

    rows = []
    for r, gs in enumerate(guess_scores):
        row = [
            f'<td class={css_class(gs, c)} id="cell-{r+1}-{c+1}">{gs.guess[c]}</td>'
            for c in range(WORDLE_LEN)
        ]
        rows.append(f'<tr id="row-{r+1}">' + " ".join(row) + "</tr>")
    if show_unplayed:
        for r in range(len(guess_scores), 6):
            row = [f'<td class="empty" id="cell-{r+1}-{c+1}"></td>' for c in range(WORDLE_LEN)]
            rows.append(f'<tr id="row-{r+1}">' + " ".join(row) + "</tr>")
    return '<table class="wordle">\n  ' + "\n  ".join(rows) + "\n</table>"


def render_keyboard(guess_scores: list[GuessScore]):
    ranks = dict(UNUSED=0, ABSENT=1, PRESENT=2, CORRECT=3)
    letters = {c: ranks["UNUSED"] for c in string.ascii_uppercase}
    css_classes = {v: k.lower() for k, v in ranks.items()}
    for gs in guess_scores:
        for i in range(WORDLE_LEN):
            c = gs.guess[i]
            r = ranks[gs.tiles[i].name]
            letters[c] = max(r, letters[c])
    payload = {c: css_classes[r] for c, r in letters.items()}
    return "<br>\n".join(f"{k}={v}" for k, v in payload.items())


def render_html(guess_scores: list[GuessScore], style_file: str, show_keyboard=False) -> str:
    return f"""\
<html>
<head>
    <link rel="stylesheet" href="{os.path.basename(style_file)}">
</head>
<body>
<div class="game">
    {render_html_table(guess_scores, show_unplayed=show_keyboard)}
    {render_keyboard(guess_scores) if show_keyboard else ""}
</div>
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
            print(
                render_html(namespace.guess_scores, namespace.style_file, namespace.keyboard),
                file=f,
            )
    if namespace.emoji:
        with output_file(namespace.output, ".txt") as f:
            print(render_emojis(namespace.guess_scores, namespace.game_id), file=f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
