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

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
