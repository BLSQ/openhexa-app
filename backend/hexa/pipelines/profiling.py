"""Turn the py-spy trace of a pipeline run into a profile of its pipeline code.

When `PipelineRun.enable_profiling` is set, the pipeline image records the run with py-spy in Chrome
trace format and sends it, gzip compressed, with the `uploadPipelineRunProfile` mutation. The trace
is a JSON array of events: `"ph": "B"` when a frame enters the stack of a thread and `"ph": "E"`
when it leaves it, with the process and thread ids, a timestamp in microseconds, and the function
name, file and line of the frame.

`build_profile` starts each stack at the pipeline's own code, leaving out what runs it (the
bootstrap script, the SDK and its task pool) and idle workers, and keeps everything the pipeline
code calls. It returns:

- `duration`: the length of the trace, in milliseconds.
- `frames`: frame names, `function (file.py)`, referenced by index below.
- `lanes`: one per thread that ran pipeline code, named after the tasks it ran, with the calls it
  made over time as `[frame, start, end, children]` trees (milliseconds since the start of the
  trace), for a flame chart that shows tasks running in parallel.
- `files`: the time spent on each line of the pipeline code files over the whole run, like line
  profilers report it, `{"pipeline.py": [[line, milliseconds], ...]}`. A line counts the time of
  the calls it makes, once even if it calls itself back, and threads running in parallel add up.

Process frames are named after the process command line, which holds the run config and therefore
secret parameters: they are never kept.
"""

import json
import re
import zlib
from collections import Counter
from typing import NamedTuple

# Decompressed size limit, to refuse gzip bombs. The pipeline image does not upload larger traces.
MAX_PROFILE_SIZE = 100 * 1024 * 1024

# Deep recursion in user code can produce stacks with thousands of frames.
MAX_DEPTH = 256

# Spans shorter than this share of the trace are left out of lanes: they are invisible unless
# zoomed in far, and would make the profile grow with the number of calls.
MIN_SPAN_RATIO = 0.0002

# ipykernel runs each notebook cell from a file named after a hash of its code.
NOTEBOOK_CELL = re.compile(r"/ipykernel_\d+/\d+\.py$")
NOTEBOOK_CELL_NAME = "Notebook cell"

# A complete stack starts at the entry point of its thread: the main thread or a worker process
# (`<module>`), another thread (`_bootstrap`) or `python -m` (`_run_module_as_main`).
ENTRY_POINTS = {"<module>", "_bootstrap", "_run_module_as_main"}

PROCESS_FRAME = re.compile(r'^process \d+:"')

# Anything else with an absolute path is pipeline code: the pipeline itself, workspace modules it
# imports and notebook cells. Matching libraries rather than the pipeline directory keeps this
# independent of where the image puts the code.
LIBRARY_PATH = re.compile(
    r"/(?:site|dist)-packages/|/lib/python3\.\d+/|/\.hexa_scripts/|/bin/"
)

SHORT_PATHS = [
    re.compile(r"/(?:site|dist)-packages/(?P<path>.*)$"),
    re.compile(r"/lib/python3\.\d+/(?P<path>.*)$"),
    re.compile(r"/pipeline/(?P<path>.*)$"),
    re.compile(r"/(?P<path>workspace/.*)$"),
]


class InvalidProfile(Exception):
    pass


def decompress_profile(data: bytes) -> bytes:
    """Decompress a gzip profile, raising InvalidProfile if it is invalid or too large."""
    decompressor = zlib.decompressobj(wbits=16 + zlib.MAX_WBITS)
    try:
        raw = decompressor.decompress(data, MAX_PROFILE_SIZE)
    except zlib.error as e:
        raise InvalidProfile(str(e)) from e
    if decompressor.unconsumed_tail:
        raise InvalidProfile("profile is too large")
    return raw


def build_profile(trace: bytes) -> dict:
    """Build the pipeline code profile of a py-spy Chrome trace, see the module docstring."""
    # Frame names, by index of first appearance.
    frames: dict[str, int] = {}
    line_times: Counter[tuple[str, int]] = Counter()
    threads: dict[tuple, _Thread] = {}
    start = end = main_pid = None
    for event in _read_events(trace):
        try:
            pid, tid, ts, phase = event["pid"], event["tid"], event["ts"], event["ph"]
        except (KeyError, TypeError):
            continue
        if phase not in ("B", "E") or not isinstance(ts, int | float):
            continue
        if start is None:
            start, end, main_pid = ts, ts, pid
        end = max(end, ts)
        thread = threads.get((pid, tid))
        if thread is None:
            thread = threads[(pid, tid)] = _Thread(ts, frames, line_times)
        thread.advance(ts)
        if phase == "B":
            thread.push(_parse_frame(event))
        else:
            thread.pop()

    if start is None:
        return {"duration": 0, "frames": [], "lanes": [], "files": {}}
    for thread in threads.values():
        thread.close()

    min_span = (end - start) * MIN_SPAN_RATIO
    lanes = []
    for (pid, _), thread in threads.items():
        if nodes := _prune(thread.roots, min_span, start):
            lanes.append((pid, nodes))
    lanes.sort(key=lambda lane: lane[1][0][1])
    names = list(frames)
    return {
        "duration": _ms(end - start),
        "frames": names,
        "lanes": _name_lanes(lanes, main_pid, names),
        "files": _group_by_file(line_times),
    }


def _read_events(trace: bytes):
    """Yield the events of a trace one at a time, to keep memory close to the size of the trace."""
    # py-spy can sample a stack while it is being modified and write garbage bytes.
    text = trace.decode("utf-8", errors="replace")
    decoder = json.JSONDecoder()
    index = _skip_whitespace(text, 0)
    if not text.startswith("[", index):
        raise InvalidProfile("trace is not a JSON array")
    index = _skip_whitespace(text, index + 1)
    try:
        while not text.startswith("]", index):
            event, index = decoder.raw_decode(text, index)
            yield event
            index = _skip_whitespace(text, index)
            if text.startswith(",", index):
                index = _skip_whitespace(text, index + 1)
    except json.JSONDecodeError as e:
        raise InvalidProfile(str(e)) from e


def _skip_whitespace(text: str, index: int) -> int:
    while index < len(text) and text[index].isspace():
        index += 1
    return index


class _Frame(NamedTuple):
    function: str
    file: str
    line: int | None
    is_pipeline_code: bool

    @property
    def name(self) -> str:
        return f"{self.function} ({self.file})"


class _Thread:
    """The stack of a thread, and the pipeline code frames it ran over time."""

    def __init__(self, ts, frames: dict[str, int], line_times: Counter):
        self.ts = ts
        self.frames = frames
        self.line_times = line_times
        # Process frames are None.
        self.stack: list[_Frame | None] = []
        self.changed = False
        # The pipeline code lines of the stack, as (file, line).
        self.lines: set[tuple[str, int]] = set()
        # Open calls, root first, as [frame, start, end, children] nodes.
        self.open: list[list] = []
        self.roots: list[list] = []
        # py-spy samples idle threads too, so a live thread always has a complete stack: an empty or
        # partial one is a sample py-spy failed to read. Calls that go on after it are kept as one.
        self.failed_since = None

    def push(self, frame: _Frame | None):
        self.stack.append(frame)
        self.changed = True

    def pop(self):
        if self.stack:
            self.stack.pop()
            self.changed = True

    def advance(self, ts):
        """Apply the stack changes made at the previous timestamp, before moving to `ts`."""
        if ts <= self.ts:
            return
        if self.changed:
            if not _is_failed_sample(self.stack):
                self._update_open()
            elif self.failed_since is None:
                self.failed_since = self.ts
            self.changed = False
        for key in self.lines:
            self.line_times[key] += ts - self.ts
        self.ts = ts

    def close(self):
        self.stack = []
        self._update_open()

    def _update_open(self):
        # Calls that ended during a failed sample are ended when it started.
        end = self.ts if self.failed_since is None else self.failed_since
        self.failed_since = None
        stack = _keep_pipeline_code(self.stack)[:MAX_DEPTH]
        self.lines = {
            (frame.file, frame.line)
            for frame in stack
            if frame.is_pipeline_code and frame.line
        }
        kept = [self.frames.setdefault(frame.name, len(self.frames)) for frame in stack]
        common = 0
        for node, frame in zip(self.open, kept):
            if node[0] != frame:
                break
            common += 1
        for node in self.open[common:]:
            node[2] = end
        del self.open[common:]
        for frame in kept[common:]:
            node = [frame, self.ts, self.ts, []]
            (self.open[-1][3] if self.open else self.roots).append(node)
            self.open.append(node)


def _is_failed_sample(stack: list[_Frame | None]) -> bool:
    frames = [frame for frame in stack if frame]
    if any(frame.is_pipeline_code for frame in frames):
        return False
    return not frames or frames[0].function not in ENTRY_POINTS


def _parse_frame(event: dict) -> _Frame | None:
    """Return the frame of a "B" event, or None for a process frame."""
    function = str(event.get("name"))
    args = event.get("args") or {}
    path = str(args.get("filename") or "")
    if not path and PROCESS_FRAME.match(function):
        return None
    if function == "<module>" and NOTEBOOK_CELL.search(path):
        function = NOTEBOOK_CELL_NAME
    file = next(
        (m["path"] for p in SHORT_PATHS if (m := p.search(path))),
        path.rsplit("/", 1)[-1],
    )
    line = args.get("line")
    return _Frame(
        function,
        file,
        line if isinstance(line, int) and line > 0 else None,
        path.startswith("/") and not LIBRARY_PATH.search(path),
    )


def _keep_pipeline_code(stack: list[_Frame | None]) -> list[_Frame]:
    """Keep the stack from its first pipeline frame, without process frames."""
    frames = [frame for frame in stack if frame]
    first = next(
        (i for i, frame in enumerate(frames) if frame.is_pipeline_code), len(frames)
    )
    return frames[first:]


def _prune(nodes: list[list], min_span: float, start) -> list[list]:
    return [
        [
            frame,
            _ms(begin - start),
            _ms(end - start),
            _prune(children, min_span, start),
        ]
        for frame, begin, end, children in nodes
        if end - begin >= min_span
    ]


def _group_by_file(line_times: Counter) -> dict[str, list[list]]:
    files: dict[str, list[list]] = {}
    for (file, line), us in sorted(line_times.items()):
        files.setdefault(file, []).append([line, _ms(us)])
    return files


def _name_lanes(lanes: list[tuple], main_pid, frames: list[str]) -> list[dict]:
    """Name lanes after the functions they ran at their root, which are the pipeline's tasks.

    Lanes that ran notebook cells are named "Notebook", lanes that only imported the pipeline are
    named after their process, and lanes with the same name are numbered.
    """
    names = [_lane_name(pid, nodes, main_pid, frames) for pid, nodes in lanes]
    counts, seen = Counter(names), Counter()
    named = []
    for name, (_, nodes) in zip(names, lanes):
        seen[name] += 1
        if counts[name] > 1:
            name = f"{name} #{seen[name]}"
        named.append({"name": name, "nodes": nodes})
    return named


def _lane_name(pid, nodes: list[list], main_pid, frames: list[str]) -> str:
    functions = dict.fromkeys(frames[node[0]].rsplit(" (", 1)[0] for node in nodes)
    functions.pop("<module>", None)
    if NOTEBOOK_CELL_NAME in functions:
        return "Notebook"
    if functions:
        return ", ".join(functions)
    return "Main process" if pid == main_pid else "Imports"


def _ms(us) -> float:
    return round(us / 1000, 1)
