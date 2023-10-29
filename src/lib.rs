use anyhow::{anyhow, Result};
use log::{info, trace};
use std::collections::HashSet;
use std::fmt;

pub const WORDLE_LEN: usize = 5;

#[derive(PartialEq, Copy, Clone, Debug)]
pub enum TileState {
    CORRECT, // green
    PRESENT, // yellow
    ABSENT,  // black
}

pub fn tile_state(score_tile: u8) -> Result<TileState> {
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
pub struct GuessScore {
    guess: String,
    #[allow(dead_code)]
    score: String,
    tiles: [TileState; WORDLE_LEN],
}

impl GuessScore {
    /// Parse a GUESS=SCORE string into a GuessScore, validating it.
    pub fn parse(guess_score: &str) -> Result<Self> {
        if let Some((guess, score)) = guess_score.split_once('=') {
            if guess.len() != WORDLE_LEN {
                return Err(anyhow!(
                    "Guess {:?} is not {} characters",
                    guess,
                    WORDLE_LEN
                ));
            }
            if score.len() != WORDLE_LEN {
                return Err(anyhow!(
                    "Score {:?} is not {} characters",
                    score,
                    WORDLE_LEN
                ));
            }
            let mut tiles = [TileState::CORRECT; WORDLE_LEN];
            for i in 0..WORDLE_LEN {
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
                score: score.to_owned(), // this is only occasionally used for debugging
                tiles,
            });
        } else {
            return Err(anyhow!(format!("Expected one '=' in '{guess_score}'")));
        }
    }
}

/// Convert set of letters into sorted string
pub fn letter_set(set: &HashSet<u8>) -> String {
    let mut letters: Vec<char> = set.iter().map(|c| *c as char).collect();
    letters.sort();
    letters.iter().collect()
}

pub fn letter_sets(sets: &Vec<HashSet<u8>>) -> String {
    format!(
        "[{}]",
        sets.iter()
            .map(|set| letter_set(set))
            .collect::<Vec<String>>()
            .join(",")
    )
}

pub fn dash_mask(mask: &[u8]) -> String {
    mask.iter()
        .map(|m| if *m != b'\0' { *m as char } else { '-' })
        .collect()
}

/// The state derived from several GuessScores
pub struct WordleGuesses {
    valid: HashSet<u8>,
    invalid: HashSet<u8>,
    mask: [u8; WORDLE_LEN],
    wrong_spot: Vec<HashSet<u8>>, // WORDLE_LEN elements
}

impl fmt::Debug for WordleGuesses {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        // The remaining letters of the alphabet that are neither valid nor invalid
        let unused: HashSet<u8> = HashSet::<u8>::from_iter(b'A'..=b'Z')
            .difference(&self.valid)
            .map(|c| *c)
            .collect::<HashSet<u8>>()
            .difference(&self.invalid)
            .map(|c| *c)
            .collect::<HashSet<u8>>();
        f.debug_struct("WordleGuesses")
            .field("mask", &dash_mask(&self.mask))
            .field("valid", &letter_set(&self.valid))
            .field("invalid", &letter_set(&self.invalid))
            .field("wrong_spot", &letter_sets(&self.wrong_spot))
            .field("unused", &letter_set(&unused))
            .finish()
    }
}

impl WordleGuesses {
    /// Parse several GuessScores into a WordleGuesses
    pub fn parse(guess_scores: &Vec<GuessScore>) -> Result<Self> {
        let mut valid: HashSet<u8> = HashSet::new();
        let mut invalid: HashSet<u8> = HashSet::new();
        let mut mask: [u8; WORDLE_LEN] = [b'\0'; WORDLE_LEN];
        let mut wrong_spot: Vec<HashSet<u8>> = (0..WORDLE_LEN).map(|_| HashSet::new()).collect();

        for gs in guess_scores {
            // First pass for correct and present
            for i in 0..WORDLE_LEN {
                let g: u8 = gs.guess.as_bytes()[i];
                let t = gs.tiles[i];
                if t == TileState::CORRECT {
                    mask[i] = g;
                    valid.insert(g);
                } else if t == TileState::PRESENT {
                    wrong_spot[i].insert(g);
                    valid.insert(g);
                }
            }
            // Second pass for absent letters
            for i in 0..WORDLE_LEN {
                if gs.tiles[i] == TileState::ABSENT {
                    let g: u8 = gs.guess.as_bytes()[i];
                    if valid.contains(&g) {
                        // There are more instances of `g` in `gs.guess`
                        // than in the answer
                        wrong_spot[i].insert(g);
                    } else {
                        invalid.insert(g);
                    }
                }
            }
        }
        Ok(Self {
            valid,
            invalid,
            mask,
            wrong_spot,
        })
    }

    /// Is `word` a candidate solution?
    pub fn is_eligible(&self, word: &str) -> bool {
        let letters: HashSet<u8> = word.bytes().collect();
        trace!("word={}, letters={:?}", word, letters);
        if letters.intersection(&self.valid).count() != self.valid.len() {
            trace!("!Valid: {}", word);
            return false;
        } else if !letters.is_disjoint(&self.invalid) {
            trace!("Invalid: {}", word);
            return false;
        } else {
            for i in 0..WORDLE_LEN {
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

    /// Find all the eligible `words`
    pub fn find_eligible(&self, words: &Vec<String>) -> Vec<String> {
        info!("{:?}", self);
        words
            .iter()
            .filter(|w| self.is_eligible(w))
            .cloned()
            .collect()
    }
}
