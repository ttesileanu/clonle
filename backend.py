""" Define the back end of the gam. """

import pandas as pd
import numpy as np

from string import ascii_lowercase
from typing import Union
from enum import Enum


class NotInitializedError(Exception):
    pass


class ClonleState(Enum):
    """Enum describing the state of a letter: unknown; contained, but unknown location;
    contained, and known location."""

    UNKNOWN = 0  # no information yet
    CONTAINED = 1  # in word, location not found
    LOCATED = 2  # in word, location found


class ClonleBackend:
    """Class that manages the wordle-like backend.

    :param database: word database; file name or Pandas dataframe
    :param length: word length
    :param frequency_cutoff: cutoff for word frequencies: any word with a frequency
        below the cutoff will be ignored; note that frequencies are calculated before
        restricting the number of letters
    :param max_attempts: maximum number of attempts
    :param rng: random number generator to use; should be either a seed or a
        `numpy.random.Generator` object

    Attributes:
        attempts: int or None
            Number of attempts made. Set to `None` before `start()`.
        state: dict or None
            Information state: dictionary indicating the state for each letter. See
            the `ClonleState` enum. Set to `None` before `start()`.
    """

    def __init__(
        self,
        database: Union[str, pd.DataFrame],
        length: int,
        frequency_cutoff: float = 0.4e-5,
        max_attempts: int = 6,
        rng: Union[int, np.random.Generator] = 0,
    ):
        self.length = length
        self.frequency_cutoff = frequency_cutoff
        self.max_attempts = max_attempts

        self.attempts = None
        self.state = None
        self.rng = np.random.default_rng(rng)

        self.database = self._clean_db(database)

    def get_state(self) -> dict:
        if self.state is None:
            raise NotInitializedError("get_state() called before start()")

        return self.state

    def start(self):
        """Start a new game.

        This chooses a target word and resets the state to indicate that no letters have
        been guessed and no attempts have been made.
        """
        self.attempts = 0
        self._reset_state()
        self.target = self._select_target()

    def _reset_state(self):
        self.state = {}
        for ch in ascii_lowercase:
            self.state[ch] = ClonleState.UNKNOWN

    def _select_word(self):
        pass

    def _clean_db(self, database: pd.DataFrame) -> pd.DataFrame:
        """Return a cleaned database, with the proper number of letters and after
        removing extremely rare words."""
        clean_db = database.copy()
        clean_db["freq"] = clean_db["count"] / clean_db["count"].sum()

        mask1 = clean_db["word"].str.len() == self.length
        mask2 = clean_db["freq"] > self.frequency_cutoff

        return clean_db[mask1 & mask2]

    def _select_target(self) -> str:
        """Select a target word."""
        return self.database["word"].sample().iloc[0]
