# CLONLE -- a wordle clone

![version](https://img.shields.io/badge/version-v1.0.0-blue)
[![Python 3.8](https://img.shields.io/badge/python-3.8-yellow.svg)](https://www.python.org/downloads/release/python-380/)
[![license: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A very simple implementation of a wordle-like game with a text-based interface.

In its default form, the goal of the game is to guess a 5-letter word. You are allowed 6
attempts, each of which must itself be a valid 5-letter word. For each attempt, the game
indicates which letters matched the target word in both identity and position; which
letters from the guessed word appear in the target word but in a different place; and
which letters are not contained in the target at all.

This implementation allows different word lengths to be chosen.

**Features:**

* can change word length
* can change the maximum number of attempts allowed
* has several options for the frequency with which a new word is chosen (daily,
hourly, or for every run).

The dictionary is from
[Kaggle: English word frequency](https://www.kaggle.com/rtatman/english-word-frequency).
Only a very basic attempt was made to clean up the dataset: a cutoff was placed on the
frequency of the words. This still leaves a lot of oddities, such as proper names, in
the database. The target words are chosen using an even more strigent frequency cutoff,
to help ensure that targets are well-known words.

## Installation

Create a fresh virtual environment and run

    pip install -r requirements.txt

## Usage

Run

    python clonle.py

...and enjoy!

Use

    python clonle.py --help

to get a description of the possible command-line options.
