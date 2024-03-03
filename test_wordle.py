#!/usr/bin/env python3

from __future__ import annotations

import pytest

from wordle import WordleGuesses


@pytest.mark.parametrize(
    "answer,guess,expected",
    [
        ("RIDGE", "OUGHT", "..g.."),
        ("RIDGE", "GRAVE", "gr..E"),
        ("RIDGE", "MERGE", "..rGE"),
    ],
)
def test_score(answer: str, guess: str, expected: str):
    computed = WordleGuesses.score(answer, guess)
    assert computed == expected


if __name__ == "__main__":
    pytest.main()
