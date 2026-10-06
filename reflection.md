# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

The first time I ran `python -m streamlit run app.py` the game *looked* finished — a
title, a difficulty selector in the sidebar, a guess box, a score, even a "Developer
Debug Info" panel that shows the secret number. Nothing crashed. That turned out to be
the most misleading part: every bug in this app fails silently, so the UI keeps looking
confident while it lies to you.

I played two games and found two bugs just by following the hints:

- **Game 1 — the hints contradicted each other.** I guessed 10 and it said "Go LOWER".
  I guessed 8 and it said "Go HIGHER". If both of those were true, the secret had to be
  9 — so I guessed 9, and it did *not* say I won. It told me "Go LOWER" again. There is
  no number that satisfies all three hints, so at least one of them was lying.
- **Game 2 — the hint pointed the wrong way.** The secret was 79 (I could see it in the
  Developer Debug Info panel). I guessed 65, which is too low, and the game told me
  "Go LOWER" — the exact opposite direction of the answer.

When I dug into the code with my AI assistant to find out *why*, the two symptoms turned
out to come from two separate bugs, and they also exposed several more I hadn't run
into while playing:

1. **The hint messages are swapped.** "Too High" prints "Go HIGHER!" and "Too Low"
   prints "Go LOWER!", so following the hint walks you away from the answer.
2. **The secret number changes type on every other guess.** `app.py` does
   `secret = str(st.session_state.secret)` whenever the attempt count is even. Comparing
   an `int` to a `str` raises `TypeError`, and `check_guess` catches that exception and
   silently falls back to comparing the numbers *as text*. `"9" > "50"` is `True`
   alphabetically, so single-digit guesses are reported as too high.
3. **"New Game" doesn't actually start a new game.** It resets the attempt counter and
   the secret but never resets `st.session_state.status`, so once you lose, the app hits
   `st.stop()` on every rerun and you are locked out permanently.
4. **The score is wrong in two separate ways** — winning on the first guess awards 80
   instead of 100, and a wrong "Too High" guess *adds* 5 points on even-numbered attempts.
5. **The difficulty setting is cosmetic.** The secret is generated once from whatever
   difficulty you loaded with and is never regenerated, so switching to Easy (range 1–20)
   can leave a secret of 87 in place — unwinnable.
6. **`logic_utils.py` was never written.** All four functions are
   `raise NotImplementedError` stubs, so the three starter tests fail immediately.

**Bug Reproduction Log**

The first two rows are what I hit while playing; the rest I reproduced afterwards once I
knew where to look (using the debug panel and by calling the functions directly).

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Game 1: guesses `10`, then `8`, then `9` | Hints that are consistent with one secret number | `10` → "Go LOWER", `8` → "Go HIGHER", `9` → "Go LOWER" (not a win) — no secret fits all three | none (a `TypeError` is raised and silently swallowed by `check_guess`) |
| Game 2: guess `65`, secret `79` | "Go HIGHER" (65 is below 79) | "Go LOWER" — hint points away from the answer | none |
| `pytest tests/` on the starter code | 3 starter tests pass | All 3 fail before asserting anything | `NotImplementedError: Refactor this function from app.py into logic_utils.py` |
| Guess the secret correctly on attempt 1 | Score of 100 | Score of 80 | none |
| Guess `60` (secret `50`) on attempt 2 | Score decreases for a wrong guess | Score **increases** by 5 | none |
| Click "New Game 🔁" after running out of attempts | A fresh, playable game | "Game over. Start a new game to try again." on every rerun, forever | none |
| Set Difficulty to "Easy" (range 1–20) mid-session | Secret is regenerated inside 1–20 | Debug panel still shows a secret of 87; sidebar claims "Range: 1 to 20" | none |
| Type `abc` into the guess box and submit | "That is not a number", attempt not consumed | Error shown, but the attempt counter still increments | none |
| Load a fresh Normal game (8 attempts) | "Attempts left: 8" | "Attempts left: 7" | none |

---

## 2. How did you use AI as a teammate?

**Tool:** I used Claude Code inside VS Code. It could read every file in the project,
run `pytest`, and run the app with Streamlit's testing tool, so it could check its own
claims instead of only guessing from the code.

**A suggestion that was correct — explaining my Game 1 bug.** In Game 1, guesses of 10,
8 and 9 got hints that no secret number could satisfy. I asked the AI why. It explained
that this was really *two* bugs at once: on every even-numbered guess, `app.py` turned
the secret into text (`str(secret)`), so `check_guess` compared `"8"` and `"50"`
alphabetically, and on top of that the hint messages were swapped ("Too High" said
"Go HIGHER!"). Its fix was to delete the text conversion, delete the `except TypeError`
block that hid the problem, and fix the messages. I verified it three ways: a pytest that
replays my Game 1 guesses (`test_game1_hints_are_consistent`), a pytest for my Game 2
(65 vs. 79 must be "Too Low"), and replaying the game myself with the debug panel open —
every hint pointed toward the secret.

**A suggestion I did not accept as written — the first "fix" didn't fix the game.** The
AI first moved `check_guess` into `logic_utils.py`, fixed it there, and reported
"7 passed." But when I played the game, the hints were *still* backwards. I told it the
game still wasn't working, and it turned out `app.py` was still using its own old copy
of `check_guess` — the tests only checked the new copy. The AI then connected `app.py`
to the fixed function and removed the `str(secret)` lines, and the hints were correct
when I played again. This taught me that passing tests only prove the code they test;
I had to play the real game to know the bug was actually gone.

A second, smaller example: the AI drafted Section 1 of this reflection with an example
game ("I guessed 60 against a secret of 50") that never happened to me. I replaced it
with my two real games, because the bug log should describe what I actually saw.

---

## 3. Debugging and testing your fixes

**How I decided a bug was really fixed.** I only counted a bug as fixed when two things
were true: a pytest that targets that exact bug passed, *and* the bug no longer happened
when I played the real game. I learned to require both the hard way — after the first
hint fix, all the tests passed but the game still gave backwards hints, because `app.py`
was using an old copy of `check_guess` that the tests never touched. So every time, I
restarted Streamlit, opened the Developer Debug Info panel to see the secret, and
repeated what had gone wrong before.

**A test I ran and what it showed.** `test_game1_hints_are_consistent` replays my Game 1
guesses (10, then 8, then 9) against a secret of 9 and checks that the answers are
"Too High", "Too Low", and "Win". Before the fix, those same guesses gave hints that no
secret could satisfy. It showed me the comparison now treats guesses as numbers every
time, not only on odd-numbered guesses. A related test,
`test_string_secret_is_not_silently_compared_as_text`, checks that passing the secret as
text now raises an error. I liked that one because the original bug was hidden by an
`except` block — now the same mistake would crash loudly instead of quietly giving wrong
hints.

I also checked the "Attempts left" fix by playing a full game on Normal: the banner
started at 8, stayed at 8 when I typed `abc`, dropped by exactly one per real guess, and
the game ended at 0. Before the fix it showed one more attempt than I really had.

All 11 tests pass (the 3 starter tests plus 8 I added):

```
tests/test_game_logic.py::test_winning_guess PASSED
tests/test_game_logic.py::test_guess_too_high PASSED
tests/test_game_logic.py::test_guess_too_low PASSED
tests/test_game_logic.py::test_game1_hints_are_consistent PASSED
tests/test_game_logic.py::test_game2_guess_below_secret_is_too_low PASSED
tests/test_game_logic.py::test_single_digit_guess_compared_as_number PASSED
tests/test_game_logic.py::test_string_secret_is_not_silently_compared_as_text PASSED
tests/test_game_logic.py::test_first_guess_win_scores_100 PASSED
tests/test_game_logic.py::test_later_win_scores_less_but_never_below_10 PASSED
tests/test_game_logic.py::test_wrong_guess_never_increases_score PASSED
tests/test_game_logic.py::test_difficulty_ranges PASSED
============================== 11 passed in 0.01s ==============================
```

**Did AI help with the tests?** Yes. The AI wrote the new tests, and I made sure each one
was based on a bug I actually saw — two of them replay my own games. It also pointed out
that the starter tests expected `check_guess` to return just `"Win"` / `"Too High"` /
`"Too Low"`, while the original code returned a pair of (outcome, message). That's why
the hint text now lives in `app.py` and `check_guess` returns only the outcome. The AI
also ran the real app with Streamlit's testing tool (`AppTest`) to simulate whole games —
winning on the first guess, losing and clicking New Game, and switching to Easy 20 times
to check the secret always landed in 1–20.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

Every time you click a button or type in a box, Streamlit runs your whole Python file
again from the top, like refreshing a page. That means normal variables are forgotten
on every click, so anything the game needs to remember (the secret number, attempts,
score) has to go in `st.session_state`, which is like a notebook that survives each
rerun. The tricky part is that the page is drawn in order, top to bottom, during that
run: the "Attempts left" banner was wrong because it was drawn near the top, *before*
the code further down counted my guess, so it always showed the old number. Session
state also caused the New Game bug — the button reset some values but left `status`
saved as "lost" in the notebook, so every rerun saw "lost" and stopped the game again.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
   The collaboration with AI was very useful and intuitive, I will definitely use it in the future. The project helped me to go look for errors, which is very useful and also fun to do.
- What is one thing you would do differently next time you work with AI on a coding task?
   I think I will try to be more precise when asking it what to do, as sometimes my prompts weren;t as precise as they needed to be, and I had to reformulate and ask again so it did it properly.
- In one or two sentences, describe how this project changed the way you think about AI generated code.
   The project made me understand that AI is a tool that makes our work easier and more efficient, but that we still need to be able to find the right prompt. We are still telling AI what to do, and we need to make sure we know what AI is doing so we are not just getting guided by it, and we guide it
