import pytest

from logic_utils import check_guess, get_range_for_difficulty, update_score

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"

def test_game1_hints_are_consistent():
    # Replays my Game 1 (guesses 10, 8, 9). With secret 9 the hints must agree:
    # 10 is too high, 8 is too low, and 9 wins -- before the fix 9 said "Go LOWER".
    assert check_guess(10, 9) == "Too High"
    assert check_guess(8, 9) == "Too Low"
    assert check_guess(9, 9) == "Win"

def test_game2_guess_below_secret_is_too_low():
    # Replays my Game 2: guessing 65 when the secret is 79 must be "Too Low".
    assert check_guess(65, 79) == "Too Low"

def test_single_digit_guess_compared_as_number():
    # Compared as text, "8" > "50" is True. As numbers, 8 is below 50.
    assert check_guess(8, 50) == "Too Low"

def test_string_secret_is_not_silently_compared_as_text():
    # The old code caught TypeError and fell back to a text comparison.
    # A str secret is a caller bug and should fail loudly instead.
    with pytest.raises(TypeError):
        check_guess(8, "50")

def test_first_guess_win_scores_100():
    # Was 80 because of an off-by-one: 100 - 10 * (attempt_number + 1).
    assert update_score(0, "Win", 1) == 100

def test_later_win_scores_less_but_never_below_10():
    assert update_score(0, "Win", 3) == 80
    assert update_score(0, "Win", 50) == 10

def test_wrong_guess_never_increases_score():
    # "Too High" used to ADD 5 points on even-numbered attempts.
    for attempt in range(1, 9):
        assert update_score(0, "Too High", attempt) == -5
        assert update_score(0, "Too Low", attempt) == -5

def test_difficulty_ranges():
    assert get_range_for_difficulty("Easy") == (1, 20)
    assert get_range_for_difficulty("Normal") == (1, 100)
    assert get_range_for_difficulty("Hard") == (1, 50)
