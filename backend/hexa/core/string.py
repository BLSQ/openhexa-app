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
