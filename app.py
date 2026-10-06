import random
import streamlit as st

from logic_utils import check_guess, get_range_for_difficulty, parse_guess, update_score

# FIX: check_guess moved to logic_utils.py with Claude Code. It now returns only the
# outcome, and the hint text lives here with the right direction for each outcome
# (the old version told you to go HIGHER when your guess was already too high).
HINT_MESSAGES = {
    "Win": "🎉 Correct!",
    "Too High": "📉 Go LOWER!",
    "Too Low": "📈 Go HIGHER!",
}

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# FIX: One place that resets EVERY piece of game state, built with Claude Code.
# New Game used to reset only attempts and the secret (leaving status "lost", so the
# game stayed locked), and it ignored the difficulty range. Attempts start at 0 --
# starting at 1 silently took away one of the player's guesses.
def start_new_game():
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.difficulty = difficulty


# FIX: Also start a new game when the difficulty changes. The secret used to be picked
# once and kept, so switching to Easy (1-20) could leave a secret of 87 -- unwinnable.
if st.session_state.get("difficulty") != difficulty:
    start_new_game()

st.subheader("Make a guess")

# FIX: Reserve the banner's spot here but fill it in at the END of the script
# (show_attempts_left), after the current guess has been counted. Drawing it here
# showed the count from before the guess -- always one more than the player had.
# Also uses the real difficulty range instead of a hardcoded "1 and 100".
attempts_box = st.empty()


def show_attempts_left():
    attempts_box.info(
        f"Guess a number between {low} and {high}. "
        f"Attempts left: {attempt_limit - st.session_state.attempts}"
    )

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    start_new_game()
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    show_attempts_left()
    st.stop()

if submit:
    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        # FIX: Count the attempt only once the guess is valid, so typing "abc"
        # no longer uses up one of the player's guesses.
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        # FIX: Removed the even-attempt str(secret) cast (found with Claude Code). The
        # secret is always compared as a number now, so guesses like 10, 8, 9 get
        # hints that agree with each other.
        outcome = check_guess(guess_int, st.session_state.secret)
        message = HINT_MESSAGES[outcome]

        if show_hint:
            st.warning(message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

show_attempts_left()

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
