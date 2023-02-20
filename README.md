# Wordle Word Finder

Given a series of Wordle guesses, find the words that can fit.

* `ADIEU=a.i.. CLOTH=c....` *includes* `MAGIC`
* `RAISE=r...e CLOUT=.L... NYMPH=..... ELVER=EL.ER` *includes* `ELDER`
* `GRAIL=.RA.. TRACK=.RAc. CRAMP=CRA.. CRABS=CRA.. CRAZY=CRAZ.` *includes* `CRAZE`
* `ARISE=.r.se ROUTE=R.u.e RULES=Ru.eS` *includes* `REBUS`
* `CHAIR=Cha.. CLASH=C.a.h CATCH=CA.ch` *includes* `CACHE`
* `SATIN=s..i. ROUGH=.o...` *includes* `KIOSK`
* `AROSE=a..se LANES=.a.es WAGES=wa.es` *includes* `SWEAT`

The command line arguments are a series of `GUESS=RESULT` pairs.
* A capital letter in `RESULT` means an exact match at that position (Green).
* A lowercase letter means the letter is in the wrong position (Yellow).
* A dot means the letter is not present (Gray).

For `TRACK=.RAc.`,
the `R` and `A` are in the correct positions (i.e., green),
the `c` is in the wrong position (yellow),
and there is no `T` or `K` (gray).

Implementations are in Python (`wordle.py`) and Rust (`src/main.rs`).

The strings in `wordle.txt` were extracted from `wordle.blahblah.js`.
You can also use `/usr/share/dict/words`.

In addition, various statistics are computed in `startwords.py`,
which really should be converted to an Jupyter notebook with graphs.
