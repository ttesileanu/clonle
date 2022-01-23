#! /usr/bin/env python

import argparse
import os

import pandas as pd

from backend import ClonleBackend, ClonleState, GameOverError
from colorama import Style, Fore, Back


def parse_command_line():
    parser = argparse.ArgumentParser(description="Clonle -- Wordle clone")
    parser.add_argument(
        "n_letters", nargs="?", default=5, help="number of letters per word"
    )
    parser.add_argument("--max-attempts", default=6, help="maximum number of attempts")

    args = parser.parse_args()
    return args


def display_state(state: dict):
    """Show the state as a colored list of letters."""
    letters = sorted(state.keys())
    mapping = {
        ClonleState.UNKNOWN: Style.RESET_ALL + Style.DIM,
        ClonleState.CONTAINED: Style.RESET_ALL + Back.YELLOW + Fore.BLACK,
        ClonleState.LOCATED: Style.RESET_ALL + Back.GREEN + Fore.WHITE,
    }
    print(Style.RESET_ALL, end="")
    for ch in letters:
        if state[ch] != ClonleState.MISSING:
            print(mapping[state[ch]] + f" {ch} ", end="")
        else:
            print(Style.RESET_ALL + "   ", end="")

    print(Style.RESET_ALL)


def display_word(word: str, res: str):
    print("   ", end="")
    for ch, score in zip(word, res):
        print(color_mapping[score] + ch, end="")
    print(Style.RESET_ALL)


def display_history(history: list):
    for item in history:
        display_word(*item)


if __name__ == "__main__":
    args = parse_command_line()
    print(f"Playing Clonle with {args.n_letters}-letter words.")
    print()

    print("Loading word database...", end="")
    database_name = os.path.join("data", "unigram_freq.csv")
    database = pd.read_csv(database_name)
    clonle = ClonleBackend(database, args.n_letters, max_attempts=args.max_attempts)
    print(" done.")

    print("Choosing a word...", end="")
    clonle.start()
    print(" done.")

    color_mapping = {
        ".": Style.RESET_ALL + Back.YELLOW + Fore.BLACK,
        "x": Style.RESET_ALL + Back.GREEN + Fore.WHITE,
        " ": Style.RESET_ALL + Style.DIM,
    }

    history = []

    while True:
        print(f"Attempt {clonle.attempts + 1} of {args.max_attempts}:")

        display_state(clonle.get_state())

        print()
        display_history(history)
        s = input(">> ")

        try:
            res = clonle.attempt(s)
            display_word(s, res)
            history.append((s, res))
        except ValueError as err:
            print(f"Invalid word: {err}")

        if res == clonle.length * "x":
            print()
            print(
                f"Success! Word found in "
                f"{clonle.attempts} / {clonle.max_attempts} attempts:"
            )
            print()
            display_history(history)
            print()
            break

        if clonle.attempts == clonle.max_attempts:
            print("Unfortunately, maximum attempts reached and word not found.")
            print(f"The word was: {clonle.target}.")
            print()
            break
