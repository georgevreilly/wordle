use std::collections::HashSet;
use std::fs;
use std::io;

// const WORD_FILE: &str = "/usr/share/dict/words";
const WORD_FILE: &str = "wordle.txt";
const LEN: usize = 5;

fn solve(words: &Vec<String>, guesses: &Vec<String>) -> Vec<String> {
    let mut valid: HashSet<char> = HashSet::new();
    let mut invalid: HashSet<char> = HashSet::new();
    let mut mask: [char; LEN] = ['\0'; LEN];
    let mut wrong_spot: Vec<HashSet<char>> = (0..LEN).map(|_| HashSet::new()).collect();
    for guess in guesses {
        if let Some((word, result)) = guess.split_once("=") {
            for i in 0..LEN {
                let w: char = word.as_bytes()[i].into();
                let r: char = result.as_bytes()[i].into();
                if 'A' <= r && r <= 'Z' {
                    valid.insert(w);
                    mask[i] = w;
                } else if 'a' <= r && r <= 'z' {
                    valid.insert(w);
                    wrong_spot[i].insert(w);
                } else if r == '.' {
                    invalid.insert(w);
                }
            }
        }
    }
    println!("valid: {:?}", valid);
    println!("invalid: {:?}", invalid);
    println!("mask: {:?}", mask);
    println!("wrong_spot: {:?}", wrong_spot);
    let mut choices: Vec<String> = Vec::new();
    for w in words {
        let letters: HashSet<char> = w.chars().collect();
        // println!("word={}, letters={:?}", w, letters);
        if letters.intersection(&valid).count() != valid.len() {
            // println!("!Valid: {}", w);
        } else if !letters.is_disjoint(&invalid) {
            // println!("Invalid: {}", w);
        } else {
            let mut ok = true;
            for i in 0..LEN {
                let c: char = w.as_bytes()[i].into();
                if mask[i] != '\0' && c != mask[i] {
                    // println!("!Mask: {}", w);
                    ok = false;
                    break;
                } else if wrong_spot[i].contains(&c) {
                    // println!("WrongSpot: {}", w);
                    ok = false;
                    break;
                }
            }
            if ok {
                // println!("Got: {}", w);
                choices.push(w.to_owned());
            }
        }
    }
    choices
}

fn main() -> io::Result<()> {
    let words = fs::read_to_string(WORD_FILE)?
        .lines()
        .filter(|w| w.len() == LEN)
        .map(|w| w.to_uppercase())
        .collect::<Vec<String>>();
    //println!("{:?}", words.as_slice()[0..20].to_vec());
    let _crazy_guesses: Vec<String> = vec![
        "GRAIL=.RA..".into(),
        "TRACK=.RAc.".into(),
        "CRAMP=CRA..".into(),
        "CRABS=CRA..".into(),
        "CRAZY=CRAZ.".into(),
    ];
    let _elder_guesses: Vec<String> = vec![
        "RAISE=r...e".into(),
        "CLOUT=.L...".into(),
        "NYMPH=.....".into(),
        "ELVER=EL.ER".into(),
    ];
    let _cache_guesses: Vec<String> = vec![
        "CHAIR=Cha..".into(),
        "CLASH=C.a.h".into(),
        "CATCH=CA.ch".into(),
    ];
    let _magic_guesses: Vec<String> = vec!["ADIEU=a.i..".into(), "CLOTH=c....".into()];

    let choices = solve(&words, &_cache_guesses);
    println!("{:?}", choices);
    Ok(())
}
