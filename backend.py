""" Define the back end of the gam. """

import pandas as pd
import numpy as np

from string import ascii_lowercase
from typing import Union, Optional
from enum import Enum


class NotInitializedError(Exception):
    pass


class GameOverError(Exception):
    pass


class ClonleState(Enum):
    """Enum describing the state of a letter: unknown; contained, but unknown location;
    contained, and known location."""

    UNKNOWN = 0  # no information yet
    CONTAINED = 1  # in word, location not found
    LOCATED = 2  # in word, location found
    MISSING = -1  # not in word


class ClonleBackend:
    """Class that manages the wordle-like backend.

    :param database: word database as a Pandas dataframe with columns "word" and "count"
    :param length: word length
    :param frequency_cutoff: cutoff for word frequencies: any word with a frequency
        below the cutoff will be ignored; frequencies are either used directly if a
        column "freq" exists, or calculated from "count" *before* restricting by word
        length
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
        database: pd.DataFrame,
        length: int,
        frequency_cutoff: Optional[float] = None,
        max_attempts: int = 6,
        rng: Union[int, np.random.Generator] = 0,
    ):
        self.length = length
        self.frequency_cutoff = frequency_cutoff
        self.max_attempts = max_attempts

        self.attempts = None
        self.state = None
        self.target = None
        self.rng = np.random.default_rng(rng)

        self.database = self._clean_db(database)

        self._target_counts = None

    def get_state(self) -> dict:
        """Return the current information state.

        :return: a dictionary in which each letter is mapped to one of the `ClonleState`
            options
        """
        if self.state is None:
            raise NotInitializedError("get_state() called before start()")

        return self.state

    def start(
        self,
        target_frequency_cutoff: Optional[float] = None,
        target_n_cutoff: Optional[int] = None,
    ):
        """Start a new game.

        This chooses a target word and resets the state to indicate that no letters have
        been guessed and no attempts have been made.

        :param target_frequency_cutoff: lowest frequency for target word
        :param target_n_cutoff: the number of top-frequency words from which to choose
            target
        """
        self.attempts = 0
        self._reset_state()
        self.target = self._select_target(
            cutoff=target_frequency_cutoff, n_cutoff=target_n_cutoff
        )
        self._setup_target_counts()

    def attempt(self, word: str) -> str:
        """Attempt a word.

        The function increases `self.attempts` and updates `self.state`.

        :param word: word to test; should be length `self.length`.
        :return: information about the word, as a string in which a space indicates no
            match; '.' indicates a letter contained in the target but not at that
            position; and 'x' indicates a letter at the correct position.
        """
        if len(word) != self.length:
            raise ValueError(
                f"attempt word has length {len(word)}, should be {self.length}."
            )
        if not str.isalpha(word):
            raise ValueError("attempt word contains non-letters.")
        if self.attempts >= self.max_attempts:
            raise GameOverError("maximum attempts made.")
        if word not in self.database["word"].values:
            raise ValueError("attempt word not in dictionary.")

        res = np.array(self.length * [" "])
        word = np.array(list(word))
        target = np.array(list(self.target))
        for ch, count in self._target_counts.items():
            # first assign `ch` to exact matches
            mask = (word == ch) & (target == ch)
            res[mask] = "x"
            n_exact = mask.sum()
            count -= n_exact

            if count == 0:
                # we found all of them
                self.state[ch] = ClonleState.LOCATED
            else:
                if n_exact > 0 and self.state[ch] != ClonleState.LOCATED:
                    # we found some, some missing/misplaced
                    self.state[ch] = ClonleState.CONTAINED

                # find remaining occurrences of `ch` in `word` (if any)
                idxs = ((word == ch) & (target != ch)).nonzero()[0][:count]

                if len(idxs) > 0:
                    if self.state[ch] != ClonleState.LOCATED:
                        self.state[ch] = ClonleState.CONTAINED
                    res[idxs] = "."

        for ch in set(word):
            if ch not in self._target_counts:
                self.state[ch] = ClonleState.MISSING

        self.attempts += 1
        return "".join(res)

    def _reset_state(self):
        self.state = {}
        for ch in ascii_lowercase:
            self.state[ch] = ClonleState.UNKNOWN

    def _clean_db(self, database: pd.DataFrame) -> pd.DataFrame:
        """Return a cleaned database, with the proper number of letters and after
        removing extremely rare words."""
        clean_db = database.copy()

        if "freq" not in clean_db.columns:
            clean_db["freq"] = clean_db["count"] / clean_db["count"].sum()

        mask = clean_db["word"].str.len() == self.length

        if self.frequency_cutoff:
            mask = mask & (clean_db["freq"] >= self.frequency_cutoff)

        return clean_db[mask].sort_values("freq", ascending=False)

    def _select_target(self, cutoff: Optional[float], n_cutoff: Optional[int]) -> str:
        """Select a target word.

        :param cutoff: lowest-frequency word to consider
        :param n_cutoff: number of top-frequency words to consider
        """
        if cutoff:
            mask = self.database["freq"] >= cutoff
            words = self.database["word"][mask]
        else:
            words = self.database["word"]

        if n_cutoff:
            words = words[:n_cutoff]
        return words.sample(random_state=self.rng).iloc[0]

    def _setup_target_counts(self):
        """Creates a `dict` member that lists the letters in `self.target` and their
        number of occurrences."""
        assert self.target is not None, "this shouldn't happen"

        counts = {}

        for ch in self.target:
            if ch in counts:
                counts[ch] += 1
            else:
                counts[ch] = 1

        self._target_counts = counts

    def __str__(self):
        return (
            f"ClonleBackend("
            f"length={self.length}, "
            f"attempts={self.attempts} / {self.max_attempts}, "
            f"target={self.target}"
            f")"
        )

    def __repr__(self):
        return (
            f"ClonleBackend("
            f"state={self.state}, "
            f"database={self.database}, "
            f"frequency_cutoff={self.frequency_cutoff}, "
            f"length={self.length}, "
            f"attempts={self.attempts}, "
            f"max_attempts={self.max_attempts}, "
            f"target={self.target}"
            f")"
        )
