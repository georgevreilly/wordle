use super::*;

#[test]
fn test_tile_state() -> Result<()> {
    assert_eq!(TileState::CORRECT, TileState::make(b'Q')?);
    assert_eq!(TileState::PRESENT, TileState::make(b'q')?);
    assert_eq!(TileState::ABSENT, TileState::make(b'.')?);
    assert!(TileState::make(b'@').is_err());
    Ok(())
}

#[test]
fn test_parse_guess_score() {
    let gs = GuessScore::parse("TRACK=.RAc.").unwrap();
    assert_eq!("TRACK", gs.guess);
    assert_eq!(".RAc.", gs.score);
    assert_eq!(
        vec![
            TileState::ABSENT,
            TileState::CORRECT,
            TileState::CORRECT,
            TileState::PRESENT,
            TileState::ABSENT
        ],
        gs.tiles
    );
    assert_eq!("⬛🟩🟩🟨⬛", gs.emojis(""));
}

#[test]
fn test_formatters() {
    let set1 = HashSet::from([b'R', b'A']);
    let set2 = HashSet::from([b'E', b'T', b'C']);
    assert_eq!("AR", letter_set(&set1));
    let sets = vec![set1, set2];
    assert_eq!("[AR,CET]", letter_sets(&sets));
    assert_eq!("-AR--", dash_mask(&[b'\0', b'A', b'R', b'\0', b'\0']));
}

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
    assert_eq!("AR..Y", WordleGuesses::score("ARRAY", "ARTSY")?);
    assert_eq!(".RR..", WordleGuesses::score("ARRAY", "ERROR")?);
    assert_eq!("r..OR", WordleGuesses::score("ERROR", "RUMOR")?);
    Ok(())
}
