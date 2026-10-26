"""Glob, grep and windowed reads over a set of text files.

The API mirrors Claude Code's Glob, Grep and Read tools, which models already know
how to drive.
"""

from .files import TextFiles
from .grep import GREP_HEAD_LIMIT, GrepOutputMode
from .path_pattern import PathPattern
from .source import MAX_TEXT_FILE_SIZE, decode_text
from .window import AGENT_READ, ReadOptions, read_window

__all__ = [
    "AGENT_READ",
    "GREP_HEAD_LIMIT",
    "MAX_TEXT_FILE_SIZE",
    "GrepOutputMode",
    "PathPattern",
    "ReadOptions",
    "TextFiles",
    "decode_text",
    "read_window",
]
