# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Describe the game's purpose.** It's a number guessing game built with Streamlit.
  The game picks a secret number in a range set by the difficulty (Easy 1–20,
  Normal 1–100, Hard 1–50). After each guess it tells you whether to go higher or
  lower, and you have a limited number of attempts (Easy 6, Normal 8, Hard 5). Winning
  in fewer guesses gives a higher score.

- [x] **Detail which bugs you found.**
  - The hints were backwards: guessing above the secret said "Go HIGHER!".
  - On every other guess, the secret was turned into text, so numbers were compared
    alphabetically (`"8"` counted as bigger than `"50"`). An `except TypeError` block
    hid the error, so the hints just quietly came out wrong.
  - "Attempts left" showed one more attempt than you really had. `attempts` started at
    1, invalid input like `abc` used up an attempt, and the banner was drawn before
    the guess was counted.
  - Scoring: winning on the first guess gave 80 instead of 100, and a wrong "Too High"
    guess *added* 5 points on even-numbered attempts.
  - "New Game" didn't reset the game status, so after losing you were stuck on
    "Game over" forever.
  - Changing the difficulty didn't pick a new secret, so on Easy (1–20) the secret
    could still be 87.
  - `logic_utils.py` had only `NotImplementedError` stubs, so all 3 starter tests failed.

- [x] **Explain what fixes you applied.**
  - Moved `check_guess`, `parse_guess`, `get_range_for_difficulty` and `update_score`
    from `app.py` into `logic_utils.py`, so they can be tested without running Streamlit.
  - `check_guess` always compares numbers and returns only `"Win"`, `"Too High"` or
    `"Too Low"`. `app.py` maps each outcome to the correct hint message.
  - `attempts` starts at 0, only valid guesses count, and the "Attempts left" banner is
    drawn at the end of the script, after the guess is counted.
  - Scoring: a first-guess win gives 100, minus 10 for each extra guess (minimum 10).
    Every wrong guess costs 5.
  - A single `start_new_game()` function resets all game state. Both the New Game
    button and changing the difficulty use it.
  - Added 8 pytest cases, one or more for each fix.

## 📸 Demo Walkthrough

A sample game on **Normal** (range 1–100, 8 attempts). In this run the secret is **63**;
you can see it by opening "Developer Debug Info".

1. The game starts and shows "Guess a number between 1 and 100. Attempts left: 8".
   Score is 0.
2. User enters **40** → hint "📈 Go HIGHER!" (40 is below 63). Attempts left: 7. Score: −5.
3. User enters **80** → hint "📉 Go LOWER!" (80 is above 63). Attempts left: 6. Score: −10.
4. User enters **abc** → error "That is not a number." Attempts left stays at **6**,
   because invalid input doesn't use up a guess.
5. User enters **63** → "🎉 Correct!", balloons, and "You won! The secret was 63.
   Final score: 70". That's 80 points for winning on the 3rd guess, minus the 10 lost
   on the two wrong guesses.
6. User clicks **New Game 🔁** → a new secret is picked, "Attempts left: 8", and the
   score resets to 0.
7. User switches Difficulty to **Easy** → a new game starts with a secret between 1 and
   20, and the banner reads "Guess a number between 1 and 20. Attempts left: 6".

## 🧪 Test Results

```
$ python -m pytest -v
collected 11 items

tests/test_game_logic.py::test_winning_guess PASSED                      [  9%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [ 18%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 27%]
tests/test_game_logic.py::test_game1_hints_are_consistent PASSED         [ 36%]
tests/test_game_logic.py::test_game2_guess_below_secret_is_too_low PASSED [ 45%]
tests/test_game_logic.py::test_single_digit_guess_compared_as_number PASSED [ 54%]
tests/test_game_logic.py::test_string_secret_is_not_silently_compared_as_text PASSED [ 63%]
tests/test_game_logic.py::test_first_guess_win_scores_100 PASSED         [ 72%]
tests/test_game_logic.py::test_later_win_scores_less_but_never_below_10 PASSED [ 81%]
tests/test_game_logic.py::test_wrong_guess_never_increases_score PASSED  [ 90%]
tests/test_game_logic.py::test_difficulty_ranges PASSED                  [100%]

============================== 11 passed in 0.01s ==============================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
