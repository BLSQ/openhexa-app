import re
import string as base_string

from django.utils.text import get_valid_filename


def remove_whitespace(original_string: str) -> str:
    return original_string.translate({ord(c): None for c in base_string.whitespace})


def generate_filename(candidate_name: str) -> str:
    valid = get_valid_filename(candidate_name)
    underscored = valid.replace("-", "_")
    dedup = re.sub(r"(_+)", "_", underscored)

    return dedup.lower()


def generate_short_name(name: str) -> str:
    """
    Generate a short_name from a name.
    Takes first letter of each word, uppercase, max 5 chars.
    If only one word, takes first 5 letters.
    """
    words = name.split()
    chars = (word[0] for word in words if word) if len(words) > 1 else name
    short_name = "".join(c for c in chars if c.isalpha())

    return short_name.upper()[:5] or "ORG"
