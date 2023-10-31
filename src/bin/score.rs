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
    for gr in &games_results {
        println!("{}: {}: {:?}", gr.game_id, gr.answer, gr.guess_scores);

        for gs in &gr.guess_scores {
            let computed = WordleGuesses::score(&gr.answer, &gs.guess)?;
            let verdict = if computed == gs.score {
                "✅ Correct"
            } else {
                "❌ Wrong!"
            };
            println!(
                "\tguess={} score={} computed={} ‹{}›  {}",
                gs.guess,
                gs.score,
                computed,
                gs.emojis(""),
                verdict
            )
        }
    }
    Ok(())
}
