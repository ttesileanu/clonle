from ssl import ALERT_DESCRIPTION_ACCESS_DENIED
import pytest

import pandas as pd

from string import ascii_lowercase
from backend import ClonleBackend, NotInitializedError, ClonleState


@pytest.fixture
def dummy_db3() -> pd.DataFrame:
    return pd.DataFrame({"word": ["foo", "bar"], "count": [4, 3]})


@pytest.fixture
def dummy_clonle3(dummy_db3) -> ClonleBackend:
    return ClonleBackend(dummy_db3, 3)


@pytest.fixture
def started_clonle3(dummy_clonle3) -> ClonleBackend:
    dummy_clonle3.start()
    return dummy_clonle3


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


def test_start_sets_target_to_a_word_from_database(started_clonle3, dummy_db3):
    assert started_clonle3.target in dummy_db3.word.tolist()
