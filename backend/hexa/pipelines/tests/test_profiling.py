import gzip
import json
from unittest.mock import patch

from django.test import SimpleTestCase

from hexa.pipelines.profiling import (
    MAX_DEPTH,
    InvalidProfile,
    build_profile,
    decompress_profile,
)

SDK = "/opt/conda/lib/python3.12/site-packages/openhexa/sdk/pipelines/task.py"
PANDAS = "/opt/conda/lib/python3.12/site-packages/pandas/core/frame.py"
PIPELINE = "/home/hexa/pipeline/pipeline.py"
SECRET_PROCESS = 'process 1:"python bootstrap.py --config=c2VjcmV0"'


def begin(ts, name, path="", pid=1, tid=1, line=1):
    return {
        "args": {"filename": path, "line": line},
        "cat": "py-spy",
        "name": name,
        "ph": "B",
        "pid": pid,
        "tid": tid,
        "ts": ts,
    }


def end(ts, pid=1, tid=1):
    return {"ph": "E", "pid": pid, "tid": tid, "ts": ts}


def trace(*events):
    return json.dumps(list(events)).encode()


def task(pid, start, stop, name):
    return [
        begin(start, f'process {pid}:"worker --config=c2VjcmV0"', pid=pid),
        begin(start, "run", SDK, pid=pid),
        begin(start, name, PIPELINE, pid=pid),
        end(stop, pid=pid),
        end(stop, pid=pid),
        end(stop, pid=pid),
    ]


class BuildProfileTest(SimpleTestCase):
    def test_starts_stacks_at_pipeline_code(self):
        profile = build_profile(
            trace(
                begin(0, SECRET_PROCESS),
                begin(0, "run", SDK, line=20),
                begin(1000, "compute", PIPELINE, line=30),
                begin(2000, "groupby", PANDAS, line=40),
                begin(2000, "_inner", PANDAS, line=50),
                end(5000),
                end(5000),
                end(6000),
                end(6000),
                end(6000),
            )
        )

        self.assertEqual(
            profile,
            {
                "duration": 6.0,
                "frames": [
                    "compute (pipeline.py)",
                    "groupby (pandas/core/frame.py)",
                    "_inner (pandas/core/frame.py)",
                ],
                "lanes": [
                    {
                        "name": "compute",
                        "nodes": [
                            [
                                0,
                                1.0,
                                6.0,
                                [[1, 2.0, 5.0, [[2, 2.0, 5.0, []]]]],
                            ]
                        ],
                    }
                ],
                "files": {"pipeline.py": [[30, 5.0]]},
            },
        )

    def test_parallel_workers(self):
        profile = build_profile(
            trace(
                begin(0, SECRET_PROCESS),
                begin(0, "run", SDK),
                *task(3, 2000, 9000, "report"),
                *task(2, 1000, 5000, "compute"),
                *task(4, 1000, 8000, "compute"),
                *task(5, 1000, 8000, "wait"),
                end(10000),
                end(10000),
            )
        )

        self.assertEqual(
            [
                (lane["name"], [node[1:3] for node in lane["nodes"]])
                for lane in profile["lanes"]
            ],
            [
                ("compute #1", [[1.0, 5.0]]),
                ("compute #2", [[1.0, 8.0]]),
                ("wait", [[1.0, 8.0]]),
                ("report", [[2.0, 9.0]]),
            ],
        )
        self.assertNotIn("c2VjcmV0", json.dumps(profile))

    def test_names_lanes(self):
        profile = build_profile(
            trace(
                begin(0, "<module>", PIPELINE, tid=1),
                end(500, tid=1),
                begin(0, "<module>", PIPELINE, pid=2),
                end(500, pid=2),
                begin(500, "fetch", PIPELINE, pid=2),
                end(700, pid=2),
                begin(800, "report", PIPELINE, pid=2),
                end(1000, pid=2),
                begin(0, "<module>", PIPELINE, pid=3),
                end(1000, pid=3),
            )
        )

        self.assertEqual(
            [lane["name"] for lane in profile["lanes"]],
            ["Main process", "fetch, report", "Imports"],
        )

    def test_notebook_cells(self):
        cell = "/tmp/ipykernel_42/{}.py"
        profile = build_profile(
            trace(
                begin(0, SECRET_PROCESS),
                begin(0, "run_cell", SDK),
                begin(0, "<module>", cell.format(1111)),
                begin(0, "crunch", cell.format(2222), line=3),
                end(2_000_000),
                end(2_000_000),
                begin(2_000_000, "<module>", cell.format(3333)),
                end(3_000_000),
                end(3_000_000),
                end(3_000_000),
            )
        )

        self.assertEqual(
            profile["frames"],
            [
                "Notebook cell (1111.py)",
                "crunch (2222.py)",
                "Notebook cell (3333.py)",
            ],
        )
        self.assertEqual(
            profile["lanes"],
            [
                {
                    "name": "Notebook",
                    "nodes": [
                        [0, 0.0, 2000.0, [[1, 0.0, 2000.0, []]]],
                        [2, 2000.0, 3000.0, []],
                    ],
                }
            ],
        )

    def test_sums_time_per_file_line(self):
        profile = build_profile(
            trace(
                begin(0, "main", PIPELINE, line=3),
                begin(0, "fib", PIPELINE, line=10),
                begin(0, "fib", PIPELINE, line=10),
                end(1000),
                end(1000),
                begin(1000, "read_csv", PANDAS, line=200),
                end(3000),
                end(3000),
                begin(3000, "task", "/home/hexa/pipeline/lib/tasks.py", tid=2, line=5),
                end(4000, tid=2),
            )
        )

        self.assertEqual(
            profile["files"],
            {"pipeline.py": [[3, 3.0], [10, 1.0]], "lib/tasks.py": [[5, 1.0]]},
        )

    def test_keeps_calls_across_failed_samples(self):
        profile = build_profile(
            trace(
                begin(0, "crunch", PIPELINE),
                begin(0, "summarize", PIPELINE),
                end(1000),
                end(1000),
                begin(1100, "astype", PANDAS),
                end(1200),
                begin(1200, "crunch", PIPELINE),
                begin(1200, "summarize", PIPELINE),
                end(2000),
                begin(2500, "summarize", PIPELINE),
                end(3000),
                end(3000),
                begin(3000, "<module>", "<string>"),
                begin(3000, "run", SDK),
                end(4000),
                end(4000),
                begin(4000, "crunch", PIPELINE),
                end(5000),
            )
        )

        self.assertEqual(
            [
                (node[1:3], [child[1:3] for child in node[3]])
                for node in profile["lanes"][0]["nodes"]
            ],
            [
                ([0.0, 3.0], [[0.0, 2.0], [2.5, 3.0]]),
                ([4.0, 5.0], []),
            ],
        )

    def test_drops_short_spans(self):
        profile = build_profile(
            trace(
                begin(0, "main", PIPELINE),
                begin(1_000_000, "short", PIPELINE),
                end(1_000_100),
                end(10_000_000),
            )
        )

        self.assertEqual(profile["lanes"][0]["nodes"], [[0, 0.0, 10000.0, []]])

    def test_without_pipeline_code(self):
        profile = build_profile(trace(begin(0, "run", SDK), end(1000)))

        self.assertEqual(profile["lanes"], [])

    def test_truncates_deep_stacks(self):
        events = [begin(0, "f", PIPELINE)] * (MAX_DEPTH + 50) + [end(1000)]

        node, depth = build_profile(trace(*events))["lanes"][0]["nodes"][0], 1
        while node[3]:
            node, depth = node[3][0], depth + 1

        self.assertEqual(depth, MAX_DEPTH)

    def test_empty_trace(self):
        self.assertEqual(
            build_profile(b"[]"),
            {
                "duration": 0,
                "frames": [],
                "lanes": [],
                "files": {},
            },
        )

    def test_invalid_trace(self):
        for invalid in [b"", b"{}", b'[{"ph": "B"}', b"[1, 2"]:
            with self.subTest(invalid=invalid), self.assertRaises(InvalidProfile):
                build_profile(invalid)


class DecompressProfileTest(SimpleTestCase):
    def test_decompresses(self):
        self.assertEqual(decompress_profile(gzip.compress(b"[]")), b"[]")

    def test_invalid(self):
        with self.assertRaises(InvalidProfile):
            decompress_profile(b"not gzip")

    @patch("hexa.pipelines.profiling.MAX_PROFILE_SIZE", 10)
    def test_too_large(self):
        with self.assertRaises(InvalidProfile):
            decompress_profile(gzip.compress(b"x" * 11))
