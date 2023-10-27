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
    CORRECT,
    PRESENT,
    ABSENT,
}

#[derive(Debug)]
struct GuessScore {
    guess: String,
    #[allow(dead_code)]
    score: String,
    tiles: [TileState; LEN],
}

fn tile_state(score_tile: u8) -> Result<TileState> {
    return if (b'A'..=b'Z').contains(&score_tile) {
        Ok(TileState::CORRECT)
    } else if (b'a'..=b'z').contains(&score_tile) {
        Ok(TileState::PRESENT)
    } else if score_tile == b'.' {
        Ok(TileState::ABSENT)
    } else {
        Err(anyhow!("Invalid score {:?}", score_tile))
    };
}

fn parse_guess_score(guess_score: &str) -> Result<GuessScore> {
    if let Some((guess, score)) = guess_score.split_once('=') {
        if guess.len() != LEN {
            return Err(anyhow!(format!("Guess {guess} is not {LEN} characters")));
        }
        if score.len() != LEN {
            return Err(anyhow!(format!("Score {score} is not {LEN} characters")));
        }
        let mut tiles = [TileState::CORRECT; LEN];
        for i in 0..LEN {
            let g: u8 = guess.as_bytes()[i];
            let s: u8 = score.as_bytes()[i];
            if !(b'A'..=b'Z').contains(&g) {
                return Err(anyhow!("Guess {:?} should be uppercase", guess));
            }
            let state = tile_state(s)?;
            if state == TileState::CORRECT {
                if g != s {
                    return Err(anyhow!("Mismatch at {}: {}!={}", i + 1, guess, score));
                }
            } else if state == TileState::PRESENT {
                if s - b'a' != g - b'A' {
                    return Err(anyhow!("Mismatch at {}: {}!={}", i + 1, guess, score));
                }
            }
            tiles[i] = state
        }
        return Ok(GuessScore {
            guess: guess.to_owned(),
            score: score.to_owned(),
            tiles,
        });
    } else {
        return Err(anyhow!(format!("Expected one '=' in '{guess_score}'")));
    }
}

struct ParsedGuesses {
    valid: HashSet<u8>,
    invalid: HashSet<u8>,
    mask: [u8; LEN],
    wrong_spot: Vec<HashSet<u8>>,
}

impl ParsedGuesses {
    fn new() -> Self {
        Self {
            valid: HashSet::new(),
            invalid: HashSet::new(),
            mask: [b'\0'; LEN],
            wrong_spot: (0..LEN).map(|_| HashSet::new()).collect(),
        }
    }
}

fn parse_guesses(guess_scores: &Vec<GuessScore>) -> Result<ParsedGuesses> {
    let mut pg = ParsedGuesses::new();
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
            let g: u8 = gs.guess.as_bytes()[i];
            let t = gs.tiles[i];
            if t == TileState::ABSENT {
                if pg.valid.contains(&g) {
                    pg.wrong_spot[i].insert(g);
                } else {
                    pg.invalid.insert(g);
                }
            }
        }
    }
    Ok(pg)
}

fn solve(words: &Vec<String>, guess_scores: &Vec<GuessScore>) -> Result<Vec<String>> {
    let pg = parse_guesses(guess_scores)?;
    info!("valid: {:?}", pg.valid);
    info!("invalid: {:?}", pg.invalid);
    info!("mask: {:?}", pg.mask);
    info!("wrong_spot: {:?}", pg.wrong_spot);
    let mut choices: Vec<String> = Vec::new();
    for w in words {
        let letters: HashSet<u8> = w.bytes().collect();
        trace!("word={}, letters={:?}", w, letters);
        if letters.intersection(&pg.valid).count() != pg.valid.len() {
            trace!("!Valid: {}", w);
        } else if !letters.is_disjoint(&pg.invalid) {
            trace!("Invalid: {}", w);
        } else {
            let mut ok = true;
            for i in 0..LEN {
                let c: u8 = w.as_bytes()[i];
                if pg.mask[i] != b'\0' && c != pg.mask[i] {
                    trace!("!Mask: {}", w);
                    ok = false;
                    break;
                } else if pg.wrong_spot[i].contains(&c) {
                    trace!("WrongSpot: {}", w);
                    ok = false;
                    break;
                }
            }
            if ok {
                debug!("Got: {}", w);
                choices.push(w.to_owned());
            }
        }
    }
    Ok(choices)
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
        .map(|gs| parse_guess_score(&gs))
        .collect();
    let guess_scores = guess_scores.unwrap();
    // println!("guess_scores = {:?}", guess_scores);
    let choices = solve(&words, &guess_scores)?;
    println!(
        "{}",
        if choices.is_empty() {
            "[--None--]".to_owned()
        } else {
            choices.join("\n")
        }
    );
    Ok(())
}
