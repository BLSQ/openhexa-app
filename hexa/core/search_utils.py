import re
import typing
from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    WORD = 1
    EXACT_WORD = 2
    FILTER = 3


@dataclass(frozen=True)
class Token:
    value: str
    type: TokenType


def tokenize(
    input_string: str, valid_filter_types: typing.Sequence[str] = None
) -> typing.List[Token]:
    tokens, accu, inside = [], "", False

    def is_filter(s):
        if valid_filter_types is None:
            return False
        column_index = s.find(":")
        return column_index != -1 and s[:column_index] in valid_filter_types

    def push_token():
        nonlocal accu, tokens, inside
        if accu:
            if is_filter(accu):
                t = TokenType.FILTER
            elif inside:
                t = TokenType.EXACT_WORD
            else:
                t = TokenType.WORD
            tokens.append(Token(value=accu.lower(), type=t))
            accu = ""

    def accumulate(c):
        nonlocal accu
        accu += c

    for c in input_string:
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


def normalize_search_index(raw_search: str) -> str:
    return re.sub(r"( +)", " ", raw_search.replace("\t", " ").lower()).strip()
