use anyhow::Result;
use clap::Parser;
use std::fs;

use wordle::*;

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

fn main() -> Result<()> {
    let args = Args::parse();
    env_logger::Builder::new()
        .filter_level(args.verbose.log_level_filter())
        .init();
    let words = fs::read_to_string(WORD_FILE)?
        .lines()
        .filter(|w| w.len() == WORDLE_LEN)
        .map(|w| w.to_uppercase())
        .collect::<Vec<String>>();
    let guess_scores = args
        .guesses
        .into_iter()
        .map(|gs| GuessScore::parse(&gs))
        .collect::<Result<Vec<GuessScore>>>()?;
    let wg = WordleGuesses::parse(&guess_scores)?;
    let choices = wg.find_eligible(&words);
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
