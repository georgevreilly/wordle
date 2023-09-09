#!/usr/bin/env python3

"""Find words with repeated letters, such as ERROR, MAMMA, or ARRAY."""

import os
import string

WORDLE_LEN = 5
WORD_FILE = os.path.join(os.path.dirname(__file__), "wordle.txt")


def read_word_list(word_file: str) -> list[str]:
    with open(word_file) as f:
        return [w.upper().strip() for w in f]


def count_letters(word: str) -> list[str]:
    counts = ["" for _ in range(WORDLE_LEN + 1)]
    for ch in string.ascii_uppercase:
        if (cnt := word.count(ch)) > 0:
            counts[cnt] += ch
    return counts


def repeats() -> None:
    word_list = read_word_list(WORD_FILE)
    multiletter_words: list[list[tuple]] = [[] for _ in range(WORDLE_LEN + 1)]
    for word in word_list:
        counts = count_letters(word)
        for i in range(WORDLE_LEN, 2 - 1, -1):
            if counts[i]:
                multiletter_words[i].append((word, counts))
                break

    for i in range(WORDLE_LEN, 3 - 1, -1):
        print(i)
        for word, counts in multiletter_words[i]:
            print(f"\t{word}: {counts}")
    print("2+2")
    for word, counts in multiletter_words[2]:
        if len(counts[2]) > 1:
            print(f"\t{word}: {counts}")


if __name__ == "__main__":
    repeats()
