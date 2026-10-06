# FIX: get_range_for_difficulty, parse_guess and update_score moved here from app.py
# with Claude Code, so the game logic can be tested without running Streamlit.


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess: int, secret: int) -> str:
    """
    Compare guess to secret and return the outcome: "Win", "Too High", or "Too Low".

    Both arguments must be ints. The hint text shown to the player lives in app.py.
    """
    # FIX: Moved from app.py with Claude Code. Removed the `except TypeError` fallback
    # that compared numbers as text ("8" > "50"), and returns only the outcome so the
    # UI picks the message -- the old version paired each outcome with the wrong hint.
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number (1 = first guess)."""
    if outcome == "Win":
        # FIX: Was 100 - 10 * (attempt_number + 1), which gave 80 for a first-guess
        # win. Each guess after the first now costs 10, with a minimum of 10 points.
        points = 100 - 10 * (attempt_number - 1)
        if points < 10:
            points = 10
        return current_score + points

    # FIX: "Too High" used to ADD 5 on even attempts. Every wrong guess now costs 5,
    # whichever direction it missed in.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
