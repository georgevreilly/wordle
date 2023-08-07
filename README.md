# Wordle Word Finder

Given a series of Wordle guesses, find the words that can fit.

* `GRAIL=.RA.. TRACK=.RAc. CRAMP=CRA.. CRABS=CRA.. CRAZY=CRAZ.` yields `CRAZE`

The command-line arguments are a series of `GUESS=SCORE` pairs.
* A capital letter in `SCORE` means an exact match at that position (Green 🟩).
* A lowercase letter means the guessed letter is in the wrong position (Yellow 🟨).
* A dot means the guessed letter is not present anywhere in the word (Black/Gray ⬛/⬜).

Example: For `TRACK=.RAc.`,
the `R` and `A` are in the correct positions (i.e., green 🟩),
the `c` is in the wrong position (yellow 🟨),
and there is no `T` or `K` (gray ⬛/⬜).

Implementations are in Python (`wordle.py`, full)
and Rust (`src/main.rs`, partial).

The strings in [`wordle.txt`](./wordle.txt) were extracted from `wordle.blahblah.js`
on the [Wordle website](https://www.nytimes.com/games/wordle/index.html).
You can also use `/usr/share/dict/words`.

My previous games and scores can be found in [`games.md`](./games.md).

The [`checkguess`](./checkguess) script invokes `wordle.py`
on a guess recorded in `games.md`:
e.g., `./checkguess ACRID` or `./checkguess 697`.

The [`score.py`](./score.py) script validates
all of the `GUESS=SCORE` pairs in `games.md`.

Previous Wordle answers can be found at
[WordFinder](https://wordfinder.yourdictionary.com/wordle/answers/).

In addition, various statistics are computed in [`startwords.py`](./startwords.py),
which really should be converted to a Jupyter notebook with graphs.

For Spelling Bee, use `bee.py` with `words_alpha.txt`,
which came from https://github.com/dwyl/english-words,
or `/usr/share/dict/words`, which has fewer obscure words.
