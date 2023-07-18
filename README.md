# Wordle Word Finder

Given a series of Wordle guesses, find the words that can fit.

* 186: `GRAIL=.RA.. TRACK=.RAc. CRAMP=CRA.. CRABS=CRA.. CRAZY=CRAZ.` yields `CRAZE`
* 196: `ARISE=.r.se ROUTE=R.u.e RULES=Ru.eS` *includes* `REBUS`
* 233: `RAISE=r...e CLOUT=.L... NYMPH=..... ELVER=EL.ER` yields `ELDER`
* 607: `ADIEU=a.i.. CLOTH=c....` *includes* `MAGIC`
* 608: `CHAIR=Cha.. CLASH=C.a.h CATCH=CA.ch` *includes* `CACHE`
* 610: `SATIN=s..i. ROUGH=.o...` *includes* `KIOSK`
* 611: `AROSE=a..se LANES=.a.es WAGES=wa.es` *includes* `SWEAT`
* 614: `HARES=.A.e. CABLE=.A..E MANGE=.A.gE GAFFE=gA..E` yields `VAGUE`
* 615: `HARES=.ar.. GUILT=..... CROAK=.Roa. BRAVO=bRa.o` yields `ARBOR`
* 616: `HARES=..... BUILT=..i.t TIMID=tI... PINTO=.I.T. WITTY=.I.TY` *includes* `FIFTY`
* 617: `HEARS=...rs SCRUB=S.RU.` *includes* `SYRUP`
* 618: `CRATE=.r..E WORSE=WORSE`
* 619: `MARES=.a... FLACK=.la.k LAIKA=l..KA` *includes* `POLKA`
* 620: `FARES=...es SKITE=s...E MOUSE=MO.SE` yields `MOOSE`
* 621: `BALES=ba.e. KEBAB=.eba. REBAR=.eba. ABATE=AB..E` *includes* `ABOVE`
* 622: `MATES=.at.s STARK=Sta.. SPLAT=S..AT` *includes* `SQUAT`
* 623: `FARCE=..r.e GUILT=....t TERNS=TerN.` yields `TREND`
* 624: `LEAKS=..... MIGHT=.i..t BLITZ=..it. OPTIC=o.tIC TONIC=TO.IC` *includes* `TOXIC`
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
* 637: `PILOT=....T CHART=cha.T` *includes* `YACHT`
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
* 663: `WENCH=...c. BLIMP=..... GROUT=.r..T` yields `CARAT`
* 664: `PRATE=...te CHILD=.HI..` yields `THIEF`
* 665: `GRIMY=g...Y BUNCH=..n.. TANGY=.angY` yields `AGONY`
* 666: `CRIME=....e FLUNG=.l... STEAK=.tE..` yields `DWELT`
* 667: `STINK=..I.. BLING=..I.. CRIMP=..I.. OXIDE=..I..` *includes* `WHIFF`
* 668: `REDUX=..du. CLIMB=..... TOUGH=.OU.h` yields `HOUND`
* 669: `DEATH=...th SHIRT=.H..t` *includes* `THUMP`
* 670: `GLEAM=.Lea. BLADE=.LA.E SLATE=.LATE` *includes* `PLATE`
* 671: `BLAST=..a.. ARCED=a.... MANGY=.A..y YAHOO=yA...` yields `KAYAK`
* 672: `WHILE=....E GRAVE=.R..E TROPE=.RO.E` *includes* `BROKE`
* 673: `THREW=..... CLUMP=..u.P` *includes* `UNZIP`
* 674: `SPITE=..iT. MINTY=.I.T. FIFTH=.I.T. BRAVO=....O` yields `DITTO`
* 675: `LIVER=...ER CHUMP=..... STANK=....k POKER=.OKER` yields `JOKER`
* 676: `SLIME=...me BRAND=.r... HOMER=.omer` yields `METRO`
* 677: `VAGUE=..G.. BIGOT=.iGo. YOGIC=.OGIC` yields `LOGIC`
* 678: `FLICK=..iC. WINCE=.I.C. BIRCH=.IRC.` yields `CIRCA`
* 679: `VAPID=.a..d STRAP=..rA. RADAR=..DAR` yields `CEDAR`
* 680: `BAGEL=.a..l CLAMP=.LA.p PLANK=PLA.. PLAIT=PLA.. PLAYA=PLA.A` yields `PLAZA`
* 681: `CIDER=...er GROVE=gr..E BARGE=.ArGE` yields `RANGE`
* 682: `WHOSE=...s. CRAMP=..... NIFTY=....Y` *includes* `SULKY`
* 683: `WORLD=.OR.d` *includes* `HORDE`
* 684: `PRIME=p.... FLASH=..... JUMPY=.U.PY` *includes* `GUPPY`
* 685: `SPACE=....e GRIND=..... ETHYL=e...l JELLO=.EL.o` yields `BELOW`
* 686: `JUDGE=...ge BLIMP=..... AGENT=Agen.` yields `ANGER`
* 687: `FRAIL=....L HOTEL=ho..L` yields `GHOUL`
* 688: `EIGHT=..g.. BROAD=..oa. MANGO=.a.go` yields `AGLOW`
* 689: `MOREL=.O... GOADS=.Oa.. TOPAZ=.O.a.` yields `COCOA`
* 690: `MAGIC=...IC STOIC=.T.IC` yields `ETHIC`
* 691: `PRONE=.RO.. GROWL=.RO.. AROMA=.ROm.` yields `BROOM`
* 692: `CRAFT=c.A.. PLACE=..AC. WHACK=..ACK QUACK=..ACK` *includes* `SNACK`
* 693: `FALSE=.a... GRUNT=.r... CHIMP=c.i..` *includes* `ACRID`
* 694: `RINSE=r..s. SUGAR=S..ar SHARD=S.AR. SMART=S.AR. SCARY=SCAR.` *includes* `SCARF`
* 695: `CAUSE=CA..E` *includes* `CANOE`
* 696: `SCOPE=....E TRADE=t.a.E LATHE=LAT.E LATKE=LAT.E` yields `LATTE`
* 697: `POKER=P.k..` *includes* `PLANK`
* 698: `OTHER=o.h.r ROUGH=ro..h HOARY=ho.R.` *includes* `SHORN`
* 699: `CHAIR=...ir RIVET=ri.E. FRIED=fRIE.` *includes* `GRIEF`
* 700: `COAST=..AS. FLASH=FLAS.` yields `FLASK`
* 701: `ANGEL=a.... GRASP=.RAS. CRASH=.RASH TRASH=.RASH` yields `BRASH`
* 702: `GLINT=gli.. LOGIC=logi.` yields `IGLOO`
* 703: `SINCE=...ce CEDAR=Ce..r CRUEL=Cr.el` yields `CLERK`
* 704: `BEING=.e... DRONE=.r..e PAVER=...ER QUEER=.u.ER ULCER=U..ER USHER=U..ER` yields `UTTER`
* 705: `TRICK=..... PLANE=.la.e` *includes* `BAGEL`
* 706: `ROUND=...N. FLANK=...N. WHINE=w.INE` *includes* `SWINE`
* 707: `BUNCH=..n.. NAVEL=nA.E.` *includes* `RAMEN`
* 708: `CLOUT=..... BRISK=..Isk SKIFF=SKI..` yields `SKIMP`
* 709: `DRONE=..o.E LOUSE=.OUSE` *includes* `MOUSE`
* 710: `REBUS=.e... FLAME=.l..e WHELP=..El. LIENS=l.En.` yields `KNEEL`
* 711: `DRAKE=..a.E CABLE=.a.LE ANGLE=A.gLE` yields `AGILE`
* 712: `BRAIN=..a.. WATCH=.A... FALSE=.A... GAUDY=.A..Y JAMMY=JA..Y` yields `JAZZY`
* 713: `MODEL=m.d.. DUMPY=dUM..` yields `HUMID`
* 714: `CHASE=..a.. BADLY=.A..Y PARTY=.A..Y NAVVY=NA..Y` yields `NANNY`
* 715: `BROAD=B..a. BASIC=Bas.. BLASE=B.ASe` yields `BEAST`
* 716: `WIELD=.ie.. CRIME=..i.e INSET=iN.e.` yields `ENNUI`
* 717: `PRIDE=..... BLANK=..... MULCH=.u.c.` *includes* `SCOUT`
* 718: `ZEBRA=.e.ra CLEAR=..eaR GAMER=.A.ER` *includes* `HATER`
* 719: `JUDGE=.u... SHOUT=...u. UNZIP=u....` *includes* `CRUMB`
* 720: `MOVIE=..... CHAMP=..a.. SUGAR=s..a. NASTY=.As..` yields `BALSA`
* 721: `FRUIT=...I. MANIC=.anI. ANVIL=An.I.` yields `AGAIN`
* 722: `DOUBT=d.u.. FRAUD=.rAuD` yields `GUARD`
* 723: `BLOAT=..O.. GROVE=gRO..` *includes* `WRONG`
* 724: `SOLID=..l.. GLEAM=.L... BLUNT=.LUN. FLUNK=.LUNK CLUNK=.LUNK` yields `PLUNK`
* 725: `WHOLE=....E PRIDE=.RI.E WRITE=.RI.E GRIME=.RIME` yields `CRIME`
* 726: `BICEP=b..e. GLOBE=...BE` yields `MAYBE`
* 727: `LABOR=.a..r RAMEN=ra... WRATH=.rat. SPRAT=SpRAt` yields `STRAP`
* 728: `DECAY=..ca. CAULK=cA... MANIC=.AN.c` yields `RANCH`
* 729: `MODEL=....l CLASP=.l.s. SULKY=S.l.Y` yields `SHYLY`
* 730: `PARSE=.A... CABIN=.A... WALTZ=.A..z GAUZY=.A.z.` yields `KAZOO`
* 731: `LAUGH=..... FROND=FRO..` *includes* `FROST`
* 732: `REALM=reA.. SCARE=.cArE TRACE=.RAcE CRAVE=CRA.E` *includes* `CRANE`
* 733: `TRIBE=T...E THOSE=T..sE` yields `TASTE`
* 734: `TEMPO=te..o OTHER=ot.E.` yields `COVET`
* 735: `ACTOR=a...r GRAVE=GRA.. GRAIN=GRA.n` yields `GRAND`
* 736: `RISKY=R.... RAVEN=R..E. ROWER=RO.E.` yields `RODEO`
* 737: `PRIDE=....e STEAL=stE..` *includes* `GUEST`
* 738: `FLANK=..a..` *includes* `ABOUT`
* 739: `MIRTH=..rt. TROPE=TR... TRACK=TRAC.` yields `TRACT`
* 740: `SMOKE=....e FETID=.e.id` *includes* `DINER`
* 741: `BEACH=..a.. AGLOW=a...W` *includes* `STRAW`
* 742: `DWARF=..... GLOBE=.L.be BLESS=BLE.. BLECH=BLE..` yields `BLEEP`
* 743: `MOVIE=MO... MOODY=MO..Y` *includes* `MOSSY`
* 744: `NOISE=.O..e GOLEM=.OlE.` *includes* `HOTEL`
* 745: `SUGAR=...ar RAMEN=ra.e. HEART=.eArt TRADE=tRA.E` *includes* `IRATE`
* 746: `FORTH=.o... CLOWN=..o.n PIANO=...no DEMON=.EmOn` yields `VENOM`
* 747: `WAGER=W.... WOUND=W..nd` yields `WINDY`
* 748: `DEPTH=D..t. DIVOT=D..oT` *includes* `DONUT`
* 749: `WEIRD=we.r. SCREW=.crEw` yields `COWER`
* 750: `STEAM=.te.. TEPID=te... CHUTE=...te VOTER=..TER` yields `ENTER`
* 751: `TOWEL=.O..l LOBBY=lO..Y HOLLY=.OLLY` *includes* `FOLLY`
* 752: `TRAIN=tra.. CHART=.hart WRATH=.raTH` yields `EARTH`
* 753: `TRADE=.r... SCOUR=....r` *includes* `WHIRL`
* 754: `COVER=...er REALM=rea.. WREAK=.rea. TAPER=.A.er FAIRE=.A.rE` *includes* `BARGE`
* 755: `GRIEF=..ief FIELD=FIE.D` yields `FIEND`
* 756: `AFTER=...er REPLY=re... CHORE=C.OrE` yields `CRONE`
* 757: `FRESH=..... CLOUT=..o.t TOADY=TOa..` yields `TOPAZ`
* 758: `GRAPH=.R.p. PROUD=pRO.d` yields `DROOP`

The command-line arguments are a series of `GUESS=SCORE` pairs.
* A capital letter in `SCORE` means an exact match at that position (Green 🟩).
* A lowercase letter means the guessed letter is in the wrong position (Yellow 🟨).
* A dot means the guessed letter is not present anywhere in the word (Black/Gray ⬛/⬜).

Example: For `TRACK=.RAc.`,
the `R` and `A` are in the correct positions (i.e., green 🟩),
the `c` is in the wrong position (yellow 🟨),
and there is no `T` or `K` (gray ⬛/⬜).

In the results above,
`yields` means that there is only **one** plausible result in my opinion,
even if the tool returns several results,
while `includes` means that there are several plausible results.
A plausible result is not too obscure, is not a plural,
and if a verb, is in the present tense singular form.

Implementations are in Python (`wordle.py`, full)
and Rust (`src/main.rs`, partial).

The strings in `wordle.txt` were extracted from `wordle.blahblah.js`
on the [Wordle website](https://www.nytimes.com/games/wordle/index.html).
You can also use `/usr/share/dict/words`.

The `checkguess` script invokes `wordle.py` on a guess recorded in this `README.md`:
e.g., `./checkguess ACRID` or `./checkguess 697`.

The `score.py` script validates all of the GUESS=SCORE pairs in `README.md`.

Previous Wordle answers can be found at
[WordFinder](https://wordfinder.yourdictionary.com/wordle/answers/).

In addition, various statistics are computed in `startwords.py`,
which really should be converted to a Jupyter notebook with graphs.

For Spelling Bee, use `bee.py` with `words_alpha.txt`,
which came from https://github.com/dwyl/english-words,
or `/usr/share/dict/words`, which has fewer obscure words.
