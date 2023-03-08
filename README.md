# Wordle Word Finder

Given a series of Wordle guesses, find the words that can fit.

* `ADIEU=a.i.. CLOTH=c....` *includes* `MAGIC`
* `RAISE=r...e CLOUT=.L... NYMPH=..... ELVER=EL.ER` *includes* `ELDER`
* `GRAIL=.RA.. TRACK=.RAc. CRAMP=CRA.. CRABS=CRA.. CRAZY=CRAZ.` *includes* `CRAZE`
* `ARISE=.r.se ROUTE=R.u.e RULES=Ru.eS` *includes* `REBUS`
* `CHAIR=Cha.. CLASH=C.a.h CATCH=CA.ch` *includes* `CACHE`
* `SATIN=s..i. ROUGH=.o...` *includes* `KIOSK`
* `AROSE=a..se LANES=.a.es WAGES=wa.es` *includes* `SWEAT`
* `HARES=.A.e. CABLE=.A..E MANGE=.A.gE GAFFE=gA..E` yields `VAGUE`
* `HARES=.ar.. GUILT=..... CROAK=.Roa. BRAVO=bRa.o` yields `ARBOR`
* `HARES=..... BUILT=..i.t TIMID=tI... PINTO=.I.T. WITTY=.I.TY` *includes* `FIFTY`
* `HEARS=...rs SCRUB=S.RU.` *includes* `SYRUP`
* `CRATE=.r..E WORSE=WORSE`
* `MARES=.a... FLACK=.la.k LAIKA=l..KA` *includes* `POLKA`
* `FARES=...es SKITE=s...E MOUSE=MO.SE` yields `MOOSE`
* `BALES=ba.e. KEBAB=.eba. REBAR=.eba. ABATE=AB..E` *includes* `ABOVE`
* `MATES=.at.s STARK=Sta.. SPLAT=S..AT` *includes* `SQUAT`
* `FARCE=..r.e GUILT=....t TERNS=TerN.` yields `TREND`
* `LEAKS=..... MIGHT=.i..t BLITZ=..it. OPTIC=o.tIC TONIC=TO.IC` *includes* `TOXIC`
* `MULCH=..... TEARS=..... WINDY=.IN.Y` *includes* `PINKY`
* `ADIEU=...e. TROPE=.ro.E FORCE=.OR.E WORSE=.ORSE` *includes* `HORSE`

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
which really should be converted to a Jupyter notebook with graphs.

For Spelling Bee, use `bee.py` with `words_alpha.txt`,
which came from https://github.com/dwyl/english-words.
