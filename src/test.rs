use super::*;

#[test]
fn test_parse_game_result() {
    let line =
        "* 186: `GRAIL=.RA.. TRACK=.RAc. CRAMP=CRA.. CRABS=CRA.. CRAZY=CRAZ.` yields `CRAZE`";
    let gr = GameResult::parse_game_result(line).unwrap();
    assert_eq!(186, gr.game_id);
    assert_eq!("yields", gr.verb);
    assert_eq!("CRAZE", gr.answer);
    assert_eq!(".RAc.", gr.guess_scores[1].score);
    assert_eq!(5, gr.guess_scores.len());
}

#[test]
fn test_score() -> Result<()> {
    assert_eq!(".RAc.", WordleGuesses::score("CRAZE", "TRACK")?);
    Ok(())
}
