use clap::Parser;
use log::{debug, info, trace};
use std::collections::HashSet;
use std::fs;
use std::io;

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

fn solve(words: &Vec<String>, guesses: &Vec<String>) -> Vec<String> {
    let mut valid: HashSet<u8> = HashSet::new();
    let mut invalid: HashSet<u8> = HashSet::new();
    let mut mask: [u8; LEN] = [b'\0'; LEN];
    let mut wrong_spot: Vec<HashSet<u8>> = (0..LEN).map(|_| HashSet::new()).collect();
    for guess in guesses {
        // TODO: better validation
        if let Some((word, result)) = guess.split_once("=") {
            for i in 0..LEN {
                let w: u8 = word.as_bytes()[i];
                let r: u8 = result.as_bytes()[i];
                if b'A' <= r && r <= b'Z' {
                    valid.insert(w);
                    mask[i] = w;
                } else if b'a' <= r && r <= b'z' {
                    valid.insert(w);
                    wrong_spot[i].insert(w);
                } else if r == b'.' {
                    invalid.insert(w);
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
    choices
}

fn main() -> io::Result<()> {
    let args = Args::parse();
    println!("{:?}", args.verbose);
    env_logger::Builder::new()
        .filter_level(args.verbose.log_level_filter())
        .init();
    let words = fs::read_to_string(WORD_FILE)?
        .lines()
        .filter(|w| w.len() == LEN)
        .map(|w| w.to_uppercase())
        .collect::<Vec<String>>();
    let choices = solve(&words, &args.guesses);
    println!("{}", choices.join("\n"));
    Ok(())
}
