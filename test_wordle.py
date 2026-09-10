#!/usr/bin/env python3

from __future__ import annotations

import pytest

from common import GuessScore
from wordle import WordleGuesses


@pytest.mark.parametrize(
    "answer,guess,expected",
    [
        ("RIDGE", "OUGHT", "..g.."),
        ("RIDGE", "GRAVE", "gr..E"),
        ("RIDGE", "MERGE", "..rGE"),
        ("STEEL", "EERIE", "ee..."),
    ],
)
def test_score(answer: str, guess: str, expected: str):
    computed = WordleGuesses.score(answer, guess)
    assert computed == expected


def test_duplicate_absent_letter_caps_count():
    """A gray tile for a letter that is also yellow/green means the answer
    has exactly that many copies, not merely 'at least one'.
    """
    gs = GuessScore.make("EERIE=ee...")
    parsed = WordleGuesses.parse([gs], optimize=False)
    assert parsed.is_eligible("STEEL")
    assert parsed.is_eligible("FLEES")
    # One E (BLEST) or three E's (EERIE) must be rejected.
    assert not parsed.is_eligible("BLEST")
    assert not parsed.is_eligible("EERIE")


if __name__ == "__main__":
    pytest.main()
