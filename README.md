# CLONLE -- a wordle clone

A very simple implementation of a wordle-like game with a text-based interface.

Features:

* can change word length
* can change the maximum number of attempts allowed
* allows several options for the frequency with which a new word is chosen (daily,
hourly, or for every run).

The dictionary is from
[Kaggle: English word frequency](https://www.kaggle.com/rtatman/english-word-frequency).
Only a very basic attempt was made to clean up the dataset: a cutoff was placed on the
frequency of the words. This still leaves a lot of oddities, such as proper names, in
the database. The target words is chosen using an even more strigent frequency cutoff,
to help ensure that only well-known words are chosen as targets.

## Installation

Create a fresh virtual environment and run

    pip install -r requirements.txt

## Usage

Run

    python clonle.py

...and enjoy!
