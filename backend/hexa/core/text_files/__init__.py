"""Glob, grep and windowed reads over a set of text files.

The API mirrors Claude Code's Glob, Grep and Read tools, which models already know
how to drive.
"""

from .files import TextFiles
from .grep import GrepOutputMode
from .path_pattern import PathPattern

__all__ = ["GrepOutputMode", "PathPattern", "TextFiles"]
