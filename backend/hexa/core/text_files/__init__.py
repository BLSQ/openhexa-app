"""Glob, grep and windowed reads over a set of text files.

The API mirrors Claude Code's Glob, Grep and Read tools, which models already know
how to drive.
"""

from .files import TextFiles
from .grep import GrepOutputMode
from .path_pattern import PathPattern
from .source import MAX_TEXT_FILE_SIZE, FileSource, decode_text

__all__ = [
    "MAX_TEXT_FILE_SIZE",
    "FileSource",
    "GrepOutputMode",
    "PathPattern",
    "TextFiles",
    "decode_text",
]
