import re
from dataclasses import dataclass
from functools import cached_property
from glob import translate as translate_glob


@dataclass(frozen=True)
class PathPattern:
    """A glob pattern: `*` stays within a directory, `**` spans any depth (including
    none) and `{a,b}` lists alternatives, e.g. `**/*.js`, `src/**/*.ts`, `*.{json,yaml}`.

    All alternatives compile once into a single regex, so matching a path is one C-level
    `match` call (about 35x faster than pathlib's `full_match` over many paths).
    """

    pattern: str

    def matches(self, path: str) -> bool:
        return self._regex.match(path) is not None

    @cached_property
    def _regex(self) -> re.Pattern:
        return re.compile(
            "|".join(
                translate_glob(alternative, recursive=True, include_hidden=True)
                for alternative in self._expand_braces(self.pattern)
            )
        )

    @classmethod
    def _expand_braces(cls, pattern: str) -> list[str]:
        # glob.translate has no brace support, but `*.{js,css}` is the idiom models reach for.
        match = re.search(r"\{([^{}]*)\}", pattern)
        if match is None:
            return [pattern]
        head, tail = pattern[: match.start()], pattern[match.end() :]
        return [
            expanded
            for option in match.group(1).split(",")
            for expanded in cls._expand_braces(head + option + tail)
        ]
