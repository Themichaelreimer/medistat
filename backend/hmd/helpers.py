import string


def sanitize_cache_key(text: str) -> str:
    return "".join([c for c in text.lower() if c in string.ascii_lowercase or c in string.digits])
