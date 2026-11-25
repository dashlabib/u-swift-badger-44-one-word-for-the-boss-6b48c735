#!/usr/bin/env python3
"""One Word for the Boss -- make.fun entry.

Exactly one word describing my boss, kept in entry.txt next to
this file. This program reads those exact bytes, checks them
against the bounty gate rule by rule, and publishes them byte
for byte to /output/entry.txt.

The word: Micromanager. Every task comes back with the font
changed, the order shuffled and a meeting booked to discuss
why it was not done the way it was already done. The word is
funny because it is a job title and an accusation at once, and
true because everyone who has had one recognises the species
instantly. Candidates I considered and cut: "Deadline" (the
boss is the deadline, but the word says nothing about the
person), "Reply-All" (funny, but the hyphen makes it two words
wearing a trench coat), and "Visionary" (what the boss calls
themselves -- a roast has to come from below, not from the
boss's own LinkedIn). Micromanager won because it needs no
explanation: one word, one shared sigh.

Gate (from the kit's RULES.txt): /output/entry.txt must be UTF-8
text of 1 to 30 characters, not only white space. The entry is
modelled as a Word: the decoded text plus the facts the gate
needs about it (its length, its pieces, whether it is plain
letters), and the gate is a list of checks over that Word, so
a failure names the rule that refused the entry and the shape
of the word that broke it. The program also guards the two
silent corruptions that would waste the entry: trailing white
space a careless write would add, and a stray digit smuggled
into the word.

Run it the way the grader does:

    python3 main.py
"""

import os
import sys

ENTRY_FILE = "entry.txt"
OUT_PATH = "/output/entry.txt"
MIN_CHARS = 1
MAX_CHARS = 30


class Word:
    """The entry as a value: the decoded text plus the facts
    the gate needs about it, computed once."""

    def __init__(self, text):
        self.text = text
        self.length = len(text)
        self.pieces = text.split()
        self.is_single = len(self.pieces) == 1 and " " not in text
        self.is_plain_letters = text.isalpha()
        self.has_digit = any(ch.isdigit() for ch in text)
        self.has_trailing_space = text != text.rstrip()

    def describe(self):
        return (f"word={self.text!r} length={self.length} "
                f"single={self.is_single} "
                f"plain-letters={self.is_plain_letters}")


def gate_checks(word):
    """Yield (rule, passed, detail) for every gate rule."""
    yield ("utf-8", True, "decoded as UTF-8")
    yield ("length", MIN_CHARS <= word.length <= MAX_CHARS,
           f"{word.length} characters (need {MIN_CHARS} to {MAX_CHARS})")
    yield ("one-word", word.is_single,
           "exactly one word" if word.is_single
           else f"{len(word.pieces)} pieces, not one word")
    yield ("no-hyphen", "-" not in word.text,
           "no hyphen holding two words together")
    yield ("letters-only", word.is_plain_letters and not word.has_digit,
           "plain letters, nothing to misread")
    yield ("no-trailing-space", not word.has_trailing_space,
           "no trailing white space")
    yield ("non-blank", bool(word.text.strip()),
           "more than white space")


def validate(word):
    """Fail on the first gate check that does not pass."""
    passed = []
    for name, ok, detail in gate_checks(word):
        if not ok:
            raise SystemExit(f"gate fail [{name}]: {detail} "
                             f"({word.describe()})")
        passed.append(f"{name}={detail}")
    print(f"gate: {'; '.join(passed)}", file=sys.stderr)


def read_entry_bytes():
    """Read entry.txt as raw bytes, exactly as committed."""
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, ENTRY_FILE), "rb") as fh:
        return fh.read()


def decode_entry(data):
    """Decode the entry bytes as UTF-8, refusing anything else."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit(f"gate fail [utf-8]: {exc}") from exc


def verify_published(path, data):
    """Re-read what was written and refuse a byte mismatch."""
    with open(path, "rb") as fh:
        published = fh.read()
    if published != data:
        raise SystemExit("published entry does not match entry.txt")


def publish(data):
    """Write the bytes unchanged to /output/entry.txt, falling
    back to ./entry.txt, and verify the published bytes match."""
    try:
        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        with open(OUT_PATH, "wb") as fh:
            fh.write(data)
        path = OUT_PATH
    except OSError:
        path = os.path.join(os.getcwd(), "entry.txt")
        with open(path, "wb") as fh:
            fh.write(data)
    verify_published(path, data)
    return path


def main():
    data = read_entry_bytes()
    word = Word(decode_entry(data))
    validate(word)
    path = publish(data)
    print(f"Wrote {word.length} characters to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
