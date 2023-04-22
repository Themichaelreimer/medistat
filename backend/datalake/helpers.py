import re


def clean_str(text: str) -> str:
    """
    Cleans a string to avoid common sources of weirdness. This includes:
    - Lowercase
    - Only Alphanumeric chars are allowed. Spaces are not allowed.

    >>> clean_str("asdf%QWERTY123")
    "asdfqwerty123"
    """
    return re.sub("[\W_]+", "", text).lower()
