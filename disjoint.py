#!/usr/bin/env python3

"""Disjoint start words"""

import argparse
from collections import defaultdict

from common import (
    ANSWERS_FILE,
    WORDLE_LEN,
    argparse_wordlist,
    read_vocabulary,
    set_verbosity,
)


def parse_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description)
    parser.set_defaults(
        verbose=0,
    )
    argparse_wordlist(parser, word_file=ANSWERS_FILE, allow_individual_words=False)
    namespace = parser.parse_args()
    set_verbosity(namespace)
    return namespace


def word_letters(word: str) -> set[str]:
    return {c for c in word}


def sort_key(word: str) -> str:
    return "".join(sorted(word_letters(word)))


def eligible_anagrams(
    vocabulary: list[str], word_len: int = WORDLE_LEN
) -> dict[str, list[str]]:
    anagrams: dict[str, list[str]] = defaultdict(list)
    for word in vocabulary:
        # Include only words with distinct letters (no repeats)
        if len(word_letters(word)) == word_len:
            anagrams[sort_key(word)].append(word)
    return anagrams


def find_disjoint_words(anagrams: dict[str, list[str]]) -> list[list[str]]:
    count = 0
    seen_permutations = set()

    def search(words: list[str], available: list[str]):
        nonlocal count
        count += 1

        if not available:
            sorted_words = " ".join(sorted(words))
            if sorted_words not in seen_permutations:
                seen_permutations.add(sorted_words)
                yield words
            return

        for candidate in available:
            letters = word_letters(candidate)
            remaining = [av for av in available if not letters & word_letters(av)]
            if attempt := search(words=words + [candidate], available=remaining):
                yield from attempt

    results: list[list[str]] = []

    for disjoint_words in search(words=[], available=list(anagrams.keys())):
        if len(disjoint_words) >= 4:
            letters = {c for w in disjoint_words for c in w}
            assert len(letters) == len(disjoint_words) * WORDLE_LEN
            results.append(disjoint_words)
            print(" ".join([anagrams[w][0] for w in disjoint_words]))
    print(f"{count} calls to search")
    return results


# TODO: try using a bitset


def main() -> int:
    namespace = parse_args(description="Disjoint start words")
    vocabulary = read_vocabulary(namespace.word_file)
    anagrams = eligible_anagrams(vocabulary)
    find_disjoint_words(anagrams)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
