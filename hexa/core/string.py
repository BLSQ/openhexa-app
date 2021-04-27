import string as base_string


def remove_whitespace(original_string):
    return original_string.translate(({ord(c): None for c in base_string.whitespace}))
