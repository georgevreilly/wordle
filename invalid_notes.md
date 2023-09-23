# Problems with various attempts at Invalid handling

* `FIFTY: HARES=..... BUILT=..i.t TIMID=tI... PINTO=.I.T. WITTY=.I.TY`
  * set: [].
  * The wrong-spot T in BUILD and TIMID poisons PINTO and WITTY.
  * tiles: «FIFTY»
  * other: FIFTY JITTY KITTY ZITTY.
  * The `?ITTY` should not have been found after `WITTY`; 3:T should have excluded them.
* `WORDY: MASON=...o. OTHER=o...r ROCKY=rO..Y WORRY=WOR.Y`:
  * set: []
  * other: WORDY WORRY.
  * `WORRY` was already guessed; 4:R should have excluded.
  * tiles: «WORDY»
* `QUICK: MORAL=..... TWINE=..I.. CHICK=..ICK`
  * set: []
  * absent: []. Repeated C in CHICK
  * tiles/exclude: «QUICK» SPICK
* `EMPTY: LODGE=....e WIPER=..Pe. TEPEE=teP.. EXPAT=E.P.t`
  * set: []
  * tiles: EMPTS «EMPTY»
* `PARTY: RISKY=r...Y CRAZY=.ra.Y WEARY=..arY MARRY=.AR.Y`
  * set: []
  * tiles: BARBY BARDY BARFY BARNY HARDY HARPY LARDY PARDY PARLY «PARTY» TARDY TARTY VARDY
* `TENTH: PLANK=...n. TENOR=TEN.. TENET=TEN.t`
  * set: []
  * tiles: TENCH TENDS TENDU «TENTH» TENTS TENTY.
  * Note that TENET=TEN.t should require mask=TENT- if we were smarter.
  * other: TENCH TENDS TENDU TENES TENGE TENSE «TENTH» TENTS TENTY TENUE.
  * TENSE TENES should be precluded by the 4:E in TENET.
* `STYLE: GROAN=..... WHILE=...LE BELLE=...LE TUPLE=t..LE STELE=ST.LE`
  * set: []
  * tiles: «STYLE»
  * other: STELE STYLE.
  * Note that STELE was already guessed; 3:E should have excluded it.
* `WRITE: SABER=...er REFIT=re.it TRITE=.RITE`
  * set: []
  * tiles: URITE «WRITE»
  * other: TRITE URITE WRITE.
  * `TRITE` was already guessed; 1:T should have excluded it.
* `MOSSY: MOVIE=MO... MOODY=MO..Y`
  * set: []
  * tiles: MOAKY MOANY MOBBY MOCHY MOCKY MOGGY MOKKY MOLLY MOMMY MONTY MOPPY MOPSY MORAY MORGY «MOSSY» MOTHY MOTTY MOULY MOUSY
  * other: MOAKY MOANY MOBBY MOCHY MOCKY MOGGY MOKKY MOLLY MOMMY MONTY MOOLY MOONY MOORY MOPPY MOPSY MORAY MORGY «MOSSY» MOTHY MOTTY MOULY MOUSY.
  * `MOOLY MOONY MOORY` should have been ruled out by MOODY's 3:O.
* `POLKA: MARES=.a... FLACK=.la.k LAIKA=l..KA`
  * set: []
  * tiles: «POLKA» PULKA
* `RODEO: RISKY=R.... RAVEN=R..E. ROWER=RO.E.`
  * set: []
  * tiles: ROBED RODED «RODEO» ROLEO ROMEO ROPED ROTED ROUET ROZET
  * other: ROBED ROBER RODED «RODEO» ROGER ROLEO ROMEO ROMER ROPED ROPER ROTED ROUET ROZET.
  * Extra: ROBER ROGER ROMER ROPER should have been excluded by ROWER's 5:R.
* `UTTER: BEING=.e... DRONE=.r..e PAVER=...ER QUEER=.u.ER ULCER=U..ER USHER=U..ER`
  * set: []
  * tiles: «UTTER»
* `BELOW: SPACE=....e GRIND=..... ETHYL=e...l JELLO=.EL.o`
  * set: []
  * tiles: «BELOW»
* `UNDER: GLARE=...re STINK=...n. NERVE=ner.. BONER=..nER`
  * set: []
  * other: ENDER «UNDER».
  * The second E in NERVE should have eliminated ENDER.
  * tiles: «UNDER»
  * Note: if `BONER=..nER` is omitted, finds --None--
* `ABOVE: BALES=ba.e. KEBAB=.eba. ABATE=AB..E`
  * tiles: «ABOVE»
  * Note: if `ABATE=AB..E` is omitted, finds --None--
