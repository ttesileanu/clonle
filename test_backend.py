from dataclasses import MISSING
import pytest

import pandas as pd
import numpy as np

from string import ascii_lowercase
from backend import ClonleBackend, NotInitializedError, ClonleState, GameOverError


@pytest.fixture
def dummy_db3() -> pd.DataFrame:
    return pd.DataFrame({"word": ["foo", "bar"], "count": [4, 3]})


@pytest.fixture
def long_db5() -> pd.DataFrame:
    counts = [100] + len(ascii_lowercase) * [1]
    words = ["fooob"] + ["bar" + _ + _ for _ in ascii_lowercase]
    return pd.DataFrame({"word": words, "count": counts})


@pytest.fixture
def special_db7() -> pd.DataFrame:
    return pd.DataFrame(
        {"word": ["snorkle", "targets", "snipers", "maximum"], "count": [4, 1, 1, 1]}
    )


@pytest.fixture
def dummy_clonle3(dummy_db3) -> ClonleBackend:
    return ClonleBackend(dummy_db3, 3)


@pytest.fixture
def started_clonle3(dummy_clonle3) -> ClonleBackend:
    dummy_clonle3.start()
    return dummy_clonle3


@pytest.fixture
def clonle7(special_db7) -> ClonleBackend:
    clonle = ClonleBackend(special_db7, 7)
    clonle.start(target_frequency_cutoff=0.5)
    return clonle


def test_create(dummy_clonle3):
    pass


def test_raises_if_get_state_before_init(dummy_clonle3):
    with pytest.raises(NotInitializedError):
        dummy_clonle3.get_state()


def test_create_and_start(started_clonle3):
    pass


def test_attempts_is_none_after_create(dummy_clonle3):
    assert dummy_clonle3.attempts is None


def test_attempts_is_zero_after_start(started_clonle3):
    assert started_clonle3.attempts == 0


def test_get_state_after_start_returns_all_letters_as_unknown(started_clonle3):
    state = started_clonle3.get_state()
    for ch in ascii_lowercase:
        assert ch in state
        assert state[ch] == ClonleState.UNKNOWN

    assert len(state) == len(ascii_lowercase)


def test_create_with_custom_rng(long_db5):
    clonle1 = ClonleBackend(long_db5, 5, rng=np.random.default_rng(0))
    clonle2 = ClonleBackend(long_db5, 5, rng=np.random.default_rng(0))

    clonle1.start()
    clonle2.start()

    assert clonle1.target == clonle2.target


def test_create_default_rng_seed_is_zero(long_db5):
    clonle1 = ClonleBackend(long_db5, 5, rng=np.random.default_rng(0))
    clonle2 = ClonleBackend(long_db5, 5)

    clonle1.start()
    clonle2.start()

    assert clonle1.target == clonle2.target


def test_start_sets_target_to_a_word_from_database(started_clonle3, dummy_db3):
    assert started_clonle3.target in dummy_db3.word.tolist()


def test_frequency_cutoff_is_obeyed(dummy_db3):
    clonle = ClonleBackend(dummy_db3, 3, frequency_cutoff=0.5)
    assert len(clonle.database) == 1


def test_target_frequency_cutoff_for_start(long_db5):
    clonle = ClonleBackend(long_db5, 5)
    clonle.start(target_frequency_cutoff=0.5)
    assert clonle.target == "fooob"


def test_target_word_is_chosen_randomly(long_db5):
    clonle = ClonleBackend(long_db5, 5)
    clonle.start()
    target1 = clonle.target

    clonle.start()
    assert clonle.target != target1


def test_attempt_returns_a_string_of_correct_length(started_clonle3):
    res = started_clonle3.attempt("bar")
    assert len(res) == 3


def test_attempt_return_value_contains_space_dot_or_x(long_db5):
    clonle = ClonleBackend(long_db5, 5)
    clonle.start(target_frequency_cutoff=0.5)
    res = clonle.attempt("baroo")

    assert set(res) == {" ", ".", "x"}


def test_attempt_increments_attempts(started_clonle3):
    started_clonle3.attempt("bar")
    assert started_clonle3.attempts == 1


def test_attempt_return_correct_example_some_matches_none_perfect(clonle7):
    res = clonle7.attempt("targets")

    assert res == "  . . ."


def test_attempt_return_correct_example_some_perfect_matches(clonle7):
    res = clonle7.attempt("snipers")
    assert res == "xx  .. "


def test_attempt_return_correct_example_no_matches(clonle7):
    res = clonle7.attempt("maximum")
    assert res == "       "


def test_attempt_return_correct_duplicated_letter_single_match():
    db = pd.DataFrame({"word": ["session", "targets"], "count": [2, 1]})
    clonle = ClonleBackend(db, 7)
    clonle.start(target_frequency_cutoff=0.5)
    res = clonle.attempt("targets")
    assert res == "    . ."


def test_attempt_return_correct_duplicated_letter_all_match():
    db = pd.DataFrame({"word": ["session", "sassier"], "count": [2, 1]})
    clonle = ClonleBackend(db, 7)
    clonle.start(target_frequency_cutoff=0.5)
    res = clonle.attempt("sassier")
    assert res == "x xxx. "


def test_attempt_return_correct_duplicated_letter_some_match():
    db = pd.DataFrame({"word": ["session", "duressy"], "count": [2, 1]})
    clonle = ClonleBackend(db, 7)
    clonle.start(target_frequency_cutoff=0.5)
    res = clonle.attempt("duressy")
    assert res == "   ... "


def test_attempt_return_correct_duplicated_letter_too_many_match():
    db = pd.DataFrame({"word": ["session", "asaasss"], "count": [2, 1]})
    clonle = ClonleBackend(db, 7)
    clonle.start(target_frequency_cutoff=0.5)
    res = clonle.attempt("asaasss")
    assert res == " .  .. "


def test_attempt_raises_value_error_for_wrong_length(clonle7):
    with pytest.raises(ValueError):
        clonle7.attempt("bla")


def test_attempt_raises_value_error_for_non_alpha(clonle7):
    with pytest.raises(ValueError):
        clonle7.attempt("foobar1")


def test_attempt_raises_game_over_error_if_max_attempts_reached(clonle7):
    for _ in range(clonle7.max_attempts):
        clonle7.attempt("maximum")
    with pytest.raises(GameOverError):
        clonle7.attempt("snorkle")


def test_str(dummy_clonle3):
    s = str(dummy_clonle3)
    assert s.startswith("ClonleBackend(")
    assert s.endswith(")")


def test_repr(dummy_clonle3):
    s = repr(dummy_clonle3)
    assert s.startswith("ClonleBackend(")
    assert s.endswith(")")


def test_state_update_some_matches_none_perfect(clonle7):
    clonle7.attempt("targets")  # "  . . ."
    state = clonle7.get_state()

    assert state["r"] == ClonleState.CONTAINED
    assert state["e"] == ClonleState.CONTAINED
    assert state["s"] == ClonleState.CONTAINED

    for _ in ascii_lowercase:
        if _ in "tag":
            assert state[_] == ClonleState.MISSING, f"{_} is not missing"
        elif _ not in "res":
            assert state[_] == ClonleState.UNKNOWN, f"{_} is not unknown"


def test_state_update_some_perfect_matches(clonle7):
    clonle7.attempt("snipers")  # "xx  .. "
    state = clonle7.get_state()

    assert state["s"] == ClonleState.LOCATED
    assert state["n"] == ClonleState.LOCATED
    assert state["e"] == ClonleState.CONTAINED
    assert state["r"] == ClonleState.CONTAINED

    for _ in ascii_lowercase:
        if _ in "ip":
            assert state[_] == ClonleState.MISSING, f"{_} is not missing"
        elif _ not in "sner":
            assert state[_] == ClonleState.UNKNOWN, f"{_} is not unknown"


def test_state_update_no_matches(clonle7):
    clonle7.attempt("maximum")  # "       "
    state = clonle7.get_state()

    for _ in ascii_lowercase:
        if _ in "maxiu":
            assert state[_] == ClonleState.MISSING, f"{_} is not missing"
        else:
            assert state[_] == ClonleState.UNKNOWN, f"{_} is not unknown"


def test_state_update_duplicated_letter_single_match():
    db = pd.DataFrame({"word": ["session", "targets"], "count": [2, 1]})
    clonle = ClonleBackend(db, 7)
    clonle.start(target_frequency_cutoff=0.5)
    clonle.attempt("targets")  # "    . ."
    state = clonle.get_state()

    assert state["e"] == ClonleState.CONTAINED
    assert state["s"] == ClonleState.CONTAINED

    for _ in ascii_lowercase:
        if _ in "targ":
            assert state[_] == ClonleState.MISSING, f"{_} is not missing"
        elif _ not in "es":
            assert state[_] == ClonleState.UNKNOWN, f"{_} is not unknown"


def test_state_update_duplicated_letter_all_match():
    db = pd.DataFrame({"word": ["session", "sassier"], "count": [2, 1]})
    clonle = ClonleBackend(db, 7)
    clonle.start(target_frequency_cutoff=0.5)
    clonle.attempt("sassier")  # "x xxx. "
    state = clonle.get_state()

    assert state["s"] == ClonleState.LOCATED
    assert state["i"] == ClonleState.LOCATED
    assert state["e"] == ClonleState.CONTAINED

    for _ in ascii_lowercase:
        if _ in "ar":
            assert state[_] == ClonleState.MISSING, f"{_} is not missing"
        elif _ not in "sie":
            assert state[_] == ClonleState.UNKNOWN, f"{_} is not unknown"


def test_state_update_duplicated_letter_some_match():
    db = pd.DataFrame({"word": ["session", "duressy"], "count": [2, 1]})
    clonle = ClonleBackend(db, 7)
    clonle.start(target_frequency_cutoff=0.5)
    clonle.attempt("duressy")  # "   ... "
    state = clonle.get_state()

    assert state["s"] == ClonleState.CONTAINED
    assert state["e"] == ClonleState.CONTAINED

    for _ in ascii_lowercase:
        if _ in "dury":
            assert state[_] == ClonleState.MISSING, f"{_} is not missing"
        elif _ not in "es":
            assert state[_] == ClonleState.UNKNOWN, f"{_} is not unknown"


def test_state_update_duplicated_letter_too_many_match():
    db = pd.DataFrame({"word": ["session", "asaasss"], "count": [2, 1]})
    clonle = ClonleBackend(db, 7)
    clonle.start(target_frequency_cutoff=0.5)
    clonle.attempt("asaasss")  # " .  .. "
    state = clonle.get_state()

    assert state["s"] == ClonleState.CONTAINED

    for _ in ascii_lowercase:
        if _ == "a":
            assert state[_] == ClonleState.MISSING, f"{_} is not missing"
        elif _ != "s":
            assert state[_] == ClonleState.UNKNOWN, f"{_} is not unknown"


def test_attempt_raises_value_error_for_word_not_in_dictionary(clonle7):
    with pytest.raises(ValueError):
        clonle7.attempt("bazooka")


def test_state_gets_updated_from_contained_to_located(clonle7):
    clonle7.attempt("targets")
    assert clonle7.get_state()["s"] == ClonleState.CONTAINED

    clonle7.attempt("snipers")
    assert clonle7.get_state()["s"] == ClonleState.LOCATED


def test_attempt_return_correct_when_exact_match_after_non_match():
    db = pd.DataFrame({"word": ["cakes", "asses"], "count": [2, 1]})
    clonle = ClonleBackend(db, 5)
    clonle.start(target_frequency_cutoff=0.5)
    res = clonle.attempt("asses")
    assert res == ".  xx"


def test_state_shows_contained_if_one_exact_match_some_missed():
    db = pd.DataFrame({"word": ["sakes", "rakes"], "count": [2, 1]})
    clonle = ClonleBackend(db, 5)
    clonle.start(target_frequency_cutoff=0.5)
    clonle.attempt("rakes")

    state = clonle.get_state()
    assert state["s"] == ClonleState.CONTAINED


def test_state_shows_contained_if_one_exact_match_some_misplaced():
    db = pd.DataFrame({"word": ["sakes", "asses"], "count": [2, 1]})
    clonle = ClonleBackend(db, 5)
    clonle.start(target_frequency_cutoff=0.5)
    res = clonle.attempt("asses")

    state = clonle.get_state()
    assert state["s"] == ClonleState.CONTAINED
