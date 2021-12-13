import re
import string as base_string
from dataclasses import dataclass
from enum import Enum
from typing import List

from django.utils.text import get_valid_filename


def remove_whitespace(original_string: str) -> str:
    return original_string.translate({ord(c): None for c in base_string.whitespace})


def generate_filename(candidate_name: str) -> str:
    valid = get_valid_filename(candidate_name)
    underscored = valid.replace("-", "_")
    dedup = re.sub(r"(_+)", "_", underscored)

    return dedup.lower()


class TokenType(Enum):
    WORD = 1
    EXACT_WORD = 2
    FILTER = 3


@dataclass(frozen=True)
class Token:
    value: str
    type: TokenType


def tokenize(input: str) -> List[Token]:
    tokens, accu, inside = [], "", False

    def push_token():
        nonlocal accu, tokens, inside
        if accu:
            t = TokenType.WORD
            if ":" in accu:
                t = TokenType.FILTER
            elif inside:
                t = TokenType.EXACT_WORD
            tokens.append(Token(value=accu, type=t))
            accu = ""

    def accumulate(c):
        nonlocal accu
        accu += c

    for c in input:
        if c == " ":
            if inside:
                accumulate(c)
            else:
                push_token()
        elif c == '"':
            push_token()
            inside = not inside
        else:
            accumulate(c)
    push_token()
    return tokens
