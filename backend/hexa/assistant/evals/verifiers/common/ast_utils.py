"""Helpers for walking Python source, shared by the pipeline verifiers."""

from __future__ import annotations

import ast
from collections.abc import Iterator
from dataclasses import dataclass

PIPELINE_FILE = "pipeline.py"


@dataclass(frozen=True)
class ParsedFile:
    name: str
    tree: ast.Module | None
    syntax_error: SyntaxError | None = None


def parse_files(files: dict[str, str]) -> list[ParsedFile]:
    """Parse every Python file in the proposed file set.

    A file that does not parse yields a ParsedFile carrying the SyntaxError,
    so callers can report it rather than crash.
    """
    parsed: list[ParsedFile] = []
    for name, content in sorted(files.items()):
        if not name.endswith(".py"):
            continue
        try:
            parsed.append(ParsedFile(name=name, tree=ast.parse(content)))
        except SyntaxError as exc:
            parsed.append(ParsedFile(name=name, tree=None, syntax_error=exc))
    return parsed


def attribute_chain(node: ast.AST) -> list[str] | None:
    """Flatten `a.b.c` into ['a', 'b', 'c'], or None if the root is not a Name.

    Subscripts and calls in the middle of a chain break resolution, so those
    return None rather than a misleading partial chain.
    """
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if not isinstance(current, ast.Name):
        return None
    parts.append(current.id)
    parts.reverse()
    return parts


def iter_calls(tree: ast.Module) -> Iterator[ast.Call]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            yield node


def called_attribute(call: ast.Call) -> list[str] | None:
    """Return the attribute chain of the callee, e.g. workspace.get_dataset."""
    if not isinstance(call.func, ast.Attribute):
        return None
    return attribute_chain(call.func)


def called_name(call: ast.Call) -> str | None:
    return call.func.id if isinstance(call.func, ast.Name) else None


def first_string_arg(call: ast.Call, keyword: str | None = None) -> ast.Constant | None:
    """First positional string literal, or the named keyword if given.

    Returns the node rather than the value so findings can carry a line number.
    """
    if keyword is not None:
        for kw in call.keywords:
            if (
                kw.arg == keyword
                and isinstance(kw.value, ast.Constant)
                and isinstance(kw.value.value, str)
            ):
                return kw.value
        return None
    for arg in call.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg
    return None


def string_constants(tree: ast.Module) -> Iterator[ast.Constant]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node
