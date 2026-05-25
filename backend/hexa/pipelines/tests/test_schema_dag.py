import io
import zipfile

from hexa.core.test import TestCase
from hexa.pipelines.schema.types import resolve_pipeline_version_dag


class FakeVersion:
    def __init__(self, zip_bytes):
        self.zipfile = zip_bytes


def _zip_with_pipeline(source: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("pipeline.py", source)
    return buf.getvalue()


class ResolvePipelineVersionDagTest(TestCase):
    def test_returns_tasks_and_edges(self):
        source = (
            'from openhexa.sdk import pipeline\n'
            '@pipeline("p")\n'
            'def p():\n'
            '    b(a())\n'
            '@p.task\n'
            'def a():\n'
            '    return 1\n'
            '@p.task\n'
            'def b(x):\n'
            '    return x\n'
        )
        version = FakeVersion(_zip_with_pipeline(source))
        dag = resolve_pipeline_version_dag(version, None)
        self.assertEqual(sorted(t["name"] for t in dag["tasks"]), ["a", "b"])
        self.assertEqual(dag["edges"], [{"source": "a", "target": "b"}])

    def test_no_zipfile_returns_empty(self):
        version = FakeVersion(None)
        dag = resolve_pipeline_version_dag(version, None)
        self.assertEqual(dag, {"tasks": [], "edges": [], "outputs": []})
