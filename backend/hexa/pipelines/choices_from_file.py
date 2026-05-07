import csv
import io
import json

import yaml

from hexa.files import storage
from hexa.files.backends.exceptions import NotFound

MAX_CHOICES_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def resolve_choices_from_file(bucket_name: str, choices_from_file: dict) -> list[str]:
    """Read a workspace file and return a flat list of string choices.

    Args:
        bucket_name: The workspace's storage bucket.
        choices_from_file: The ``choices_from_file`` spec from a pipeline parameter —
            a dict with keys ``path``, ``format``, and optionally ``column``.

    Raises
    ------
        ValueError: If the file is missing, too large, unparseable, or the
            column/key cannot be resolved.
    """
    path = choices_from_file["path"].lstrip("/")
    fmt = choices_from_file["format"]
    column = choices_from_file.get("column")

    try:
        obj = storage.get_bucket_object(bucket_name, path)
    except NotFound:
        raise ValueError(f"Choices file '{path}' not found in workspace storage.")

    if obj.size > MAX_CHOICES_FILE_SIZE:
        raise ValueError(
            f"Choices file '{path}' is too large ({obj.size} bytes). "
            f"Maximum allowed size is {MAX_CHOICES_FILE_SIZE} bytes."
        )

    raw = storage.read_object(bucket_name, path)
    if len(raw) > MAX_CHOICES_FILE_SIZE:
        raise ValueError(
            f"Choices file '{path}' is too large ({len(raw)} bytes). "
            f"Maximum allowed size is {MAX_CHOICES_FILE_SIZE} bytes."
        )
    text = raw.decode("utf-8")

    if fmt == "csv":
        return _parse_csv(text, column, path)
    elif fmt == "json":
        return _parse_json(text, column, path)
    elif fmt == "yaml":
        return _parse_yaml(text, column, path)
    else:
        raise ValueError(f"Unsupported file format '{fmt}'.")


def _parse_csv(text: str, column: str | None, path: str) -> list[str]:
    """Extract choices from a CSV file.

    Supported shapes:

    - Single-column CSV (column auto-detected):
        code
        a
        b

    - Multi-column CSV (column required):
        code,label
        a,A        →  column="code"
    """
    reader = csv.DictReader(io.StringIO(text))
    fieldnames = reader.fieldnames or []

    if not fieldnames:
        raise ValueError(f"CSV file '{path}' is empty or has no header row.")

    if column is None:
        if len(fieldnames) > 1:
            raise ValueError(
                f"CSV file '{path}' has multiple columns ({', '.join(fieldnames)}). "
                "Specify a column in the ChoicesFromFile definition."
            )
        column = fieldnames[0]
    elif column not in fieldnames:
        raise ValueError(
            f"Column '{column}' not found in CSV file '{path}'. "
            f"Available columns: {', '.join(fieldnames)}."
        )

    return [row[column] for row in reader if row.get(column) is not None]


def _parse_json(text: str, column: str | None, path: str) -> list[str]:
    """Extract choices from a JSON file. See _extract_from_data for supported shapes."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse JSON file '{path}': {e}.")

    return _extract_from_data(data, column, path, "JSON")


def _parse_yaml(text: str, column: str | None, path: str) -> list[str]:
    """Extract choices from a YAML file. See _extract_from_data for supported shapes."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise ValueError(f"Could not parse YAML file '{path}': {e}.")

    return _extract_from_data(data, column, path, "YAML")


def _extract_from_data(
    data: list | dict, column: str | None, path: str, fmt: str
) -> list[str]:
    """Extract a flat list of string choices from already-parsed data.

    Supported shapes (applies to both JSON and YAML):

    - Flat array:
        ["a", "b", "c"]

    - Array of single-key objects (column auto-detected):
        [{"code": "a"}, {"code": "b"}]

    - Array of multi-key objects (column required):
        [{"code": "a", "label": "A"}, ...]  →  column="code"

    - Object wrapping an array (key auto-detected when only one key):
        {"choices": ["a", "b", "c"]}

    - Object wrapping an array (column required when multiple keys):
        {"codes": ["a", "b"], "labels": ["A", "B"]}  →  column="codes"
    """
    if isinstance(data, dict):
        keys = list(data.keys())
        if column is None:
            if len(keys) > 1:
                raise ValueError(
                    f"{fmt} file '{path}' contains multiple keys ({', '.join(keys)}). "
                    "Specify a column in the ChoicesFromFile definition."
                )
            column = keys[0]
        elif column not in data:
            raise ValueError(
                f"Key '{column}' not found in {fmt} file '{path}'. "
                f"Available keys: {', '.join(keys)}."
            )
        data = data[column]
        column = None  # consumed for the dict key; inner list uses its own detection

    if not isinstance(data, list):
        raise ValueError(
            f"{fmt} file '{path}' must contain a top-level array or an object whose values are arrays."
        )

    if not data:
        return []

    if isinstance(data[0], dict):
        if column is None:
            keys = list(data[0].keys())
            if len(keys) > 1:
                raise ValueError(
                    f"{fmt} file '{path}' contains objects with multiple keys ({', '.join(keys)}). "
                    "Specify a column in the ChoicesFromFile definition."
                )
            column = keys[0]
        return [str(item[column]) for item in data if column in item]

    return [str(item) for item in data]
