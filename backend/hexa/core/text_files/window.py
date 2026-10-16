from .lines import clip, split_lines


def read_window(
    text: str,
    start_line: int | None = None,
    end_line: int | None = None,
    *,
    line_numbers: bool = False,
    max_lines: int | None = None,
    max_line_chars: int | None = None,
) -> dict:
    """A 1-indexed, inclusive window of the text's lines, with its total line count.

    `max_lines` caps the window and adds a notice telling how to read the rest;
    `line_numbers` prefixes each line `cat -n` style; `max_line_chars` clips long lines.
    """
    lines = split_lines(text)
    total = len(lines)
    start = max(start_line or 1, 1)
    end = min(end_line or total, total)
    result = {"start_line": start, "end_line": end, "total_lines": total}

    if total == 0:
        return {**result, "content": "", "notice": "The file is empty."}
    if start > total:
        return {
            **result,
            "content": "",
            "notice": f"start_line {start} is past the end of the file ({total} lines).",
        }
    if max_lines is not None and end - start + 1 > max_lines:
        end = result["end_line"] = start + max_lines - 1
        result["notice"] = (
            f"PARTIAL view: lines {start}-{end} of {total}. Pass start_line and "
            "end_line to read another section, or grep for the content you need."
        )

    window = (clip(line, max_line_chars) for line in lines[start - 1 : end])
    if line_numbers:
        window = (f"{n:>6}\t{line}" for n, line in enumerate(window, start))
    return {**result, "content": "\n".join(window)}
