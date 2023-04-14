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
* 625: `MULCH=..... TEARS=..... WINDY=.IN.Y` *includes* `PINKY`
* 626: `ADIEU=...e. TROPE=.ro.E FORCE=.OR.E WORSE=.ORSE` *includes* `HORSE`
* 627: `CRAMP=.ra.. GUILT=g..l. LARGE=large` yields `REGAL`
* 628: `ASIDE=....E CRAMP=.r... BLUNT=..... WHORE=WH.RE` yields `WHERE`
* 629: `CRUSH=.r... GLOAM=.l... TILDE=..l.e REBEL=RE.EL` *includes* `REVEL`
* 630: `WHARF=..A.. MOULT=m..l. CLAMP=.lAm. GIBES=.i.e.` yields `EMAIL`
* 631: `GAMIN=...i. CRUSH=.r..H WORTH=..RTH BERTH=B.RTH` yields `BIRTH`
* 632: `SLANG=.LA.. GRADE=..A.E` *includes* `BLAME`
* 633: `GRAPE=.r... CLIMB=.l... WOUND=..u.. HULKS=.Ul.s` yields `SURLY`
* 634: `CLOUT=..... GRAPE=...pe WINED=w..E. SHEEP=S.EEP` yields `SWEEP`
* 635: `CRAMP=Cr... FIRST=.Ir.. CIDER=CIDER`
* 636: `GROUT=..... CHASE=..A.e PEAKY=.EA.Y BEADY=.EA.Y LEAFY=lEA.Y` *includes* `MEALY`
* 637: `PILOT=....T CHART=cha.t` *includes* `YACHT`
* 638: `STRIP=..r.. GRAND=.R..d DROVE=dRo.e ORDER=oRde.` yields `CREDO`
* 639: `PRINT=..... CLASH=.L... GLOBE=GLO.E` yields `GLOVE`
* 640: `GRIPE=g.... CLOUT=..out` *includes* `TOUGH`
* 641: `BRING=..... PLATE=...te SHOUT=...uT` *includes* `DUVET`
* 642: `WRING=..i.. PLATE=..At.` yields `STAID`
* 643: `FRAIL=.R... CRUDE=.Ru.. SHOUT=..OUT` *includes* `GROUT`
* 644: `BRAIN=.r... CLOVE=..ove` *includes* `VOTER`
* 645: `CRONE=...nE PLAIT=...It` yields `UNTIE`
* 646: `SLANG=..ANg` *includes* `GUANO`
* 647: `BRAIN=.r... CLOVE=..... SPURT=..uR. FURRY=.URRY` yields `HURRY`
* 648: `CIVET=...ET EGRET=e..ET SLEET=s.eET` *includes* `BESET`
* 649: `GRIEF=.R.e. CHEST=..E.. BREAK=BREA. BREAM=BREA.` yields `BREAD`
* 650: `SLANG=..... GROUT=.r... CHIRP=...R. MERRY=.e.RY` yields `EVERY`
* 651: `CHART=char. REACH=r.aCH` *includes* `MARCH`
* 652: `WHILE=..... CRAMP=c.... DONUT=.o..t SCOTS=ScOt.` yields `STOCK`
* 653: `FRIED=Fr... CLUMP=.L...` *includes* `FLORA`
* 654: `STRAP=.tra. UNITE=..it. TRAIL=traI.` yields `RATIO`
* 655: `FRAUD=..A.. WHALE=.hA.. STAPH=S.A.H` yields `SMASH`
* 656: `CLASP=.lA.. LEANT=LEA..` *includes* `LEAFY`
* 657: `SPLIT=s.l.. BRACE=...c. CLOGS=clo.S LOCKS=LOC.S` *includes* `LOCUS`
* 658: `MOURN=..... SCAPE=....E GLIDE=gl.dE` yields `LEDGE`
* 659: `ANGRY=aN... ENACT=.NA..` *includes* `SNAFU`
* 660: `GLARE=...re STINK=...n. NERVE=ner.. BONER=..nER` *includes* `UNDER`
* 661: `GLARE=.lA.. STALK=..AL.` yields `QUALM`
* 662: `SURLY=..R.. CORED=.OR..` *includes* `BORAX`
* 662: `WENCH=...c. BLIMP=..... GROUT=.r..T` yields `CARAT`
* 663: `PRATE=...te CHILD=.HI..` yields `THIEF`

The command-line arguments are a series of `GUESS=RESULT` pairs.
* A capital letter in `RESULT` means an exact match at that position (Green 🟩).
* A lowercase letter means the guessed letter is in the wrong position (Yellow 🟨).
* A dot means the guessed letter is not present anywhere in the word (Black/Gray ⬛/⬜).

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
