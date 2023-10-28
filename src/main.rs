use anyhow::{anyhow, Result};
use clap::Parser;
use log::{debug, info, trace};
use std::collections::HashSet;
use std::fs;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    #[clap(flatten)]
    verbose: clap_verbosity_flag::Verbosity,

    #[arg(num_args(1..), required(true))]
    guesses: Vec<String>,
}

// const WORD_FILE: &str = "/usr/share/dict/words";
const WORD_FILE: &str = "wordle.txt";
const LEN: usize = 5;

#[derive(PartialEq, Copy, Clone, Debug)]
enum TileState {
    CORRECT, // green
    PRESENT, // yellow
    ABSENT,  // black
}

fn tile_state(score_tile: u8) -> Result<TileState> {
    return if (b'A'..=b'Z').contains(&score_tile) {
        Ok(TileState::CORRECT)
    } else if (b'a'..=b'z').contains(&score_tile) {
        Ok(TileState::PRESENT)
    } else if score_tile == b'.' {
        Ok(TileState::ABSENT)
    } else {
        Err(anyhow!("Invalid score {:?}", score_tile as char))
    };
}

#[derive(Debug)]
struct GuessScore {
    guess: String,
    #[allow(dead_code)]
    score: String,
    tiles: [TileState; LEN],
}

impl GuessScore {
    fn parse(guess_score: &str) -> Result<Self> {
        if let Some((guess, score)) = guess_score.split_once('=') {
            if guess.len() != LEN {
                return Err(anyhow!("Guess {:?} is not {} characters", guess, LEN));
            }
            if score.len() != LEN {
                return Err(anyhow!("Score {:?} is not {} characters", score, LEN));
            }
            let mut tiles = [TileState::CORRECT; LEN];
            for i in 0..LEN {
                let g: u8 = guess.as_bytes()[i];
                let s: u8 = score.as_bytes()[i];
                if !(b'A'..=b'Z').contains(&g) {
                    return Err(anyhow!(
                        "Guess {:?} should be uppercase, {:?} at {}",
                        guess,
                        g as char,
                        i + 1
                    ));
                }
                tiles[i] = tile_state(s)?;
                if (tiles[i] == TileState::CORRECT && s != g)
                    || (tiles[i] == TileState::PRESENT && s - b'a' + b'A' != g)
                {
                    return Err(anyhow!(
                        "Mismatch at {}: {:?}!={:?}, {:?}!={:?}",
                        i + 1,
                        guess,
                        score,
                        g as char,
                        s as char
                    ));
                }
            }
            return Ok(Self {
                guess: guess.to_owned(),
                score: score.to_owned(),
                tiles,
            });
        } else {
            return Err(anyhow!(format!("Expected one '=' in '{guess_score}'")));
        }
    }
}

struct WordleGuesses {
    valid: HashSet<u8>,
    invalid: HashSet<u8>,
    mask: [u8; LEN],
    wrong_spot: Vec<HashSet<u8>>,
}

impl WordleGuesses {
    fn new() -> Self {
        Self {
            valid: HashSet::new(),
            invalid: HashSet::new(),
            mask: [b'\0'; LEN],
            wrong_spot: (0..LEN).map(|_| HashSet::new()).collect(),
        }
    }

    fn parse(guess_scores: &Vec<GuessScore>) -> Result<Self> {
        let mut pg = Self::new();
        for gs in guess_scores {
            // First pass for correct and present
            for i in 0..LEN {
                let g: u8 = gs.guess.as_bytes()[i];
                let t = gs.tiles[i];
                if t == TileState::CORRECT {
                    pg.mask[i] = g;
                    pg.valid.insert(g);
                } else if t == TileState::PRESENT {
                    pg.wrong_spot[i].insert(g);
                    pg.valid.insert(g);
                }
            }
            // Second pass for absent letters
            for i in 0..LEN {
                if gs.tiles[i] == TileState::ABSENT {
                    let g: u8 = gs.guess.as_bytes()[i];
                    if pg.valid.contains(&g) {
                        // There are more instances of `g` in `gs.guess`
                        // than in the answer
                        pg.wrong_spot[i].insert(g);
                    } else {
                        pg.invalid.insert(g);
                    }
                }
            }
        }
        Ok(pg)
    }

    fn is_eligible(&self, word: &str) -> bool {
        let letters: HashSet<u8> = word.bytes().collect();
        trace!("word={}, letters={:?}", word, letters);
        if letters.intersection(&self.valid).count() != self.valid.len() {
            trace!("!Valid: {}", word);
            return false;
        } else if !letters.is_disjoint(&self.invalid) {
            trace!("Invalid: {}", word);
            return false;
        } else {
            for i in 0..LEN {
                let c: u8 = word.as_bytes()[i];
                if self.mask[i] != b'\0' && c != self.mask[i] {
                    trace!("!Mask: {}", word);
                    return false;
                } else if self.wrong_spot[i].contains(&c) {
                    trace!("WrongSpot: {}", word);
                    return false;
                }
            }
        }
        true
    }

    fn find_eligible(&self, words: &Vec<String>) -> Result<Vec<String>> {
        info!("valid: {:?}", self.valid);
        info!("invalid: {:?}", self.invalid);
        info!("mask: {:?}", self.mask);
        info!("wrong_spot: {:?}", self.wrong_spot);
        let mut choices: Vec<String> = Vec::new();
        for w in words {
            if self.is_eligible(&w) {
                debug!("Got: {}", w);
                choices.push(w.to_owned());
            }
        }
        Ok(choices)
    }
}

fn main() -> Result<()> {
    let args = Args::parse();
    env_logger::Builder::new()
        .filter_level(args.verbose.log_level_filter())
        .init();
    let words = fs::read_to_string(WORD_FILE)?
        .lines()
        .filter(|w| w.len() == LEN)
        .map(|w| w.to_uppercase())
        .collect::<Vec<String>>();
    let guess_scores: Result<Vec<GuessScore>> = args
        .guesses
        .into_iter()
        .map(|gs| GuessScore::parse(&gs))
        .collect();
    let guess_scores = guess_scores?;
    let wg = WordleGuesses::parse(&guess_scores)?;
    let choices = wg.find_eligible(&words)?;
    println!(
        "{}",
        if choices.is_empty() {
            "--None--".to_owned()
        } else {
            choices.join("\n")
        }
    );
    Ok(())
}
