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
        letters = {c for c in word}
        # Exclude words with repeated letters
        if len(letters) == word_len:
            anagrams[sort_key(word)].append(word)
    return anagrams


def find_disjoint_words(anagrams: dict[str, list[str]]) -> list[list[str]]:
    seen_permutations = set()

    def helper(words: list[str], available: list[str]):
        if not available:
            sorted_words = " ".join(sorted(words))
            if sorted_words not in seen_permutations:
                seen_permutations.add(sorted_words)
                yield words
            return

        for candidate in available:
            cand_letters = word_letters(candidate)
            attempt = helper(
                words=words + [candidate],
                available=[
                    av for av in available if not cand_letters & word_letters(av)
                ],
            )
            if attempt:
                yield from attempt

    results: list[list[str]] = []

    for disjoint_words in helper(words=[], available=anagrams.keys()):
        if len(disjoint_words) >= 4:
            letters = {c for w in disjoint_words for c in w}
            assert len(letters) == len(disjoint_words) * WORDLE_LEN
            results.append(disjoint_words)
            print(" ".join([anagrams[w][0] for w in disjoint_words]))
    return results


def main() -> int:
    namespace = parse_args(description="Disjoint start words")
    vocabulary = read_vocabulary(namespace.word_file)
    anagrams = eligible_anagrams(vocabulary)
    find_disjoint_words(anagrams)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
