use anyhow::Result;
use clap::Parser;

use wordle::*;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    #[clap(flatten)]
    verbose: clap_verbosity_flag::Verbosity,
}

const GAMES_RESULTS: &str = "games.md";

fn main() -> Result<()> {
    let args = Args::parse();
    env_logger::Builder::new()
        .filter_level(args.verbose.log_level_filter())
        .init();
    let games_results = GameResult::parse_file(GAMES_RESULTS)?;
    println!("Got {} results", games_results.len());
    println!("{:?}", games_results[40]);
    Ok(())
}
