#!/usr/bin/env python3

"""Disjoint start words"""

from __future__ import annotations

import argparse
from collections import defaultdict

from common import (
    ANSWERS_FILE,
    WORDLE_LEN,
    argparse_wordlist,
    read_vocabulary,
    scrabble_score,
    set_verbosity,
    to_base,
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


def eligible_anagrams(vocabulary: list[str], word_len: int = WORDLE_LEN) -> dict[str, list[str]]:
    anagrams: dict[str, list[str]] = defaultdict(list)
    for word in vocabulary:
        # Include only words with distinct letters (no repeats)
        if len(word_letters(word)) == word_len:
            anagrams[sort_key(word)].append(word)
    return anagrams


def find_disjoint_words1(anagrams: dict[str, list[str]]) -> list[list[str]]:
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


def word_frozen_letters(word: str) -> frozenset[str]:
    return frozenset(c for c in word)


def find_disjoint_words2(anagrams: dict[str, list[str]]) -> list[list[str]]:
    count = 0
    seen_permutations = set()
    anagram_frozenset = {word_frozen_letters(k): k for k in anagrams.keys()}

    def search(words: list[str], available: list[tuple[frozenset[str], str]]):
        nonlocal count
        count += 1

        if not available:
            sorted_words = " ".join(sorted(words))
            if sorted_words not in seen_permutations:
                seen_permutations.add(sorted_words)
                yield words
            return

        for cand_set, cand_word in available:
            remaining = [av for av in available if not cand_set & av[0]]
            if attempt := search(words=words + [cand_word], available=remaining):
                yield from attempt

    results: list[list[str]] = []

    for disjoint_words in search(words=[], available=list(anagram_frozenset.items())):
        if len(disjoint_words) >= 4:
            letters = {c for w in disjoint_words for c in w}
            assert len(letters) == len(disjoint_words) * WORDLE_LEN
            results.append(disjoint_words)
            print(" ".join([anagrams[w][0] for w in disjoint_words]))
    print(f"{count} calls to search")
    return results


def word_bitset(word: str) -> int:
    bitset = 0
    for c in word:
        bitset |= 1 << (ord(c) - ord("@"))
    return bitset


def bitset_word(bitset: int) -> str:
    word = [chr(c + ord("@")) for c in range(1, 26 + 1) if bitset & (1 << c)]
    return "".join(word)


def find_disjoint_words3(anagrams: dict[str, list[str]]) -> list[list[str]]:
    count = 0
    seen_permutations = set()
    anagram_bitset = {word_bitset(k): k for k in anagrams.keys()}

    def search(wordsets: list[int], available: list[tuple[int, str]]):
        nonlocal count
        count += 1

        if not available:
            key = tuple(sorted(wordsets))
            if key not in seen_permutations:
                seen_permutations.add(key)
                yield wordsets
            return

        for cand_set, _cand_word in available:
            remaining = [av for av in available if not cand_set & av[0]]
            if attempt := search(
                wordsets=wordsets + [cand_set],
                available=remaining,
            ):
                yield from attempt

    results: list[list[str]] = []

    for disjoint_words in search(wordsets=[], available=list(anagram_bitset.items())):
        if len(disjoint_words) >= 4:
            letters = {c for w in disjoint_words for c in bitset_word(w)}
            assert (
                len(letters) == len(disjoint_words) * WORDLE_LEN
            ), f"{letters=}, {disjoint_words=}"
            results.append(disjoint_words)
            words = [anagrams[anagram_bitset[w]][0] for w in disjoint_words]
            scores = [scrabble_score(w) for w in words]
            avg_score = sum(scores) // len(scores)
            score = to_base(avg_score, 36) + "".join(to_base(s, 36) for s in scores)
            words = ["/".join(anagrams[anagram_bitset[w]]) for w in disjoint_words]
            print(score, " ".join(words))
    print(f"{count} calls to search")
    return results


def main() -> int:
    namespace = parse_args(description="Disjoint start words")
    vocabulary = read_vocabulary(namespace.word_file)
    anagrams = eligible_anagrams(vocabulary)
    find_disjoint_words3(anagrams)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
