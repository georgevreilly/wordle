#!/usr/bin/env python3

from __future__ import annotations
from typing import Literal

from wordle import WordleGuesses

import pytest


@pytest.mark.parametrize(
    "answer,guess,expected",
    [
        ("RIDGE", "OUGHT", "..g.."),
        ("RIDGE", "GRAVE", "gr..E"),
        ("RIDGE", "MERGE", "..rGE"),
    ],
)
def test_score(
    answer: Literal["RIDGE"],
    guess: Literal["OUGHT", "GRAVE", "MERGE"],
    expected: Literal["..g..", "gr..E", "..rGE"],
):
    computed = WordleGuesses.score(answer, guess)
    assert computed == expected


if __name__ == "__main__":
    pytest.main()
