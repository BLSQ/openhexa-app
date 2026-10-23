def split_lines(text: str) -> list[str]:
    # Unlike str.splitlines, only "\n" ends a line, so numbers match what editors show.
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    return lines


def clip(line: str, max_chars: int | None) -> str:
    if max_chars is None or len(line) <= max_chars:
        return line
    return f"{line[:max_chars]}… [{len(line) - max_chars} more characters]"
