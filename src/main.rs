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

fn solve(words: &Vec<String>, guesses: &Vec<String>) -> Result<Vec<String>> {
    let mut valid: HashSet<u8> = HashSet::new();
    let mut invalid: HashSet<u8> = HashSet::new();
    let mut mask: [u8; LEN] = [b'\0'; LEN];
    let mut wrong_spot: Vec<HashSet<u8>> = (0..LEN).map(|_| HashSet::new()).collect();
    for guess in guesses {
        if let Some((word, result)) = guess.split_once('=') {
            if word.len() != LEN {
                return Err(anyhow!("{:?} is not {} characters long", word, LEN));
            } else if result.len() != LEN {
                return Err(anyhow!("{:?} is not {} characters long", result, LEN));
            }
            for i in 0..LEN {
                let w: u8 = word.as_bytes()[i];
                let r: u8 = result.as_bytes()[i];
                if !(b'A'..=b'Z').contains(&w) {
                    return Err(anyhow!("{:?} should be uppercase", word));
                }
                if (b'A'..=b'Z').contains(&r) {
                    if r != w {
                        return Err(anyhow!("Mismatch at position {} between {:?} and {:?}", i, word, result));
                    }
                    valid.insert(w);
                    mask[i] = w;
                } else if (b'a'..=b'z').contains(&r) {
                    if r - b'a' != w - b'A' {
                        return Err(anyhow!("Mismatch at position {} between {:?} and {:?}", i, word, result));
                    }
                    valid.insert(w);
                    wrong_spot[i].insert(w);
                } else if r == b'.' {
                    invalid.insert(w);
                } else {
                    return Err(anyhow!("Invalid result char: {:?}", r));
                }
            }
        }
    }
    info!("valid: {:?}", valid);
    info!("invalid: {:?}", invalid);
    info!("mask: {:?}", mask);
    info!("wrong_spot: {:?}", wrong_spot);
    let mut choices: Vec<String> = Vec::new();
    for w in words {
        let letters: HashSet<u8> = w.bytes().collect();
        trace!("word={}, letters={:?}", w, letters);
        if letters.intersection(&valid).count() != valid.len() {
            trace!("!Valid: {}", w);
        } else if !letters.is_disjoint(&invalid) {
            trace!("Invalid: {}", w);
        } else {
            let mut ok = true;
            for i in 0..LEN {
                let c: u8 = w.as_bytes()[i];
                if mask[i] != b'\0' && c != mask[i] {
                    trace!("!Mask: {}", w);
                    ok = false;
                    break;
                } else if wrong_spot[i].contains(&c) {
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
    let choices = solve(&words, &args.guesses)?;
    println!("{}", choices.join("\n"));
    Ok(())
}
