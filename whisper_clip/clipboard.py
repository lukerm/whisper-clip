"""Deliver text to the system clipboard."""

import pyperclip


def copy(text: str) -> None:
    pyperclip.copy(text)
