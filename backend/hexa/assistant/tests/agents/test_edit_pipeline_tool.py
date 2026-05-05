from unittest.mock import MagicMock

from hexa.assistant.agents.edit_pipeline_agent import (
    ProposedFile,
    propose_pipeline_version,
)
from hexa.core.test import TestCase

from ._helpers import _make_zipfile


def _make_pipeline_stub(zipfile_data=None, version_name="v1"):
    version = MagicMock()
    version.zipfile = zipfile_data
    version.version_name = version_name
    pipeline = MagicMock()
    pipeline.last_version = version if zipfile_data is not None else None
    return pipeline


class ProposePipelineVersionToolTest(TestCase):
    def test_no_existing_version_returns_modified_files(self):
        pipeline = _make_pipeline_stub()
        result = propose_pipeline_version(
            pipeline,
            [ProposedFile(name="pipeline.py", content="print('hello')")],
        )
        self.assertEqual(
            result,
            {"files": [{"name": "pipeline.py", "content": "print('hello')"}]},
        )

    def test_merges_modified_file_into_existing_zip(self):
        zip_data = _make_zipfile(
            ("pipeline.py", "# original"),
            ("utils.py", "# helpers"),
        )
        pipeline = _make_pipeline_stub(zipfile_data=zip_data)
        result = propose_pipeline_version(
            pipeline,
            [ProposedFile(name="pipeline.py", content="# updated")],
        )
        files = {f["name"]: f["content"] for f in result["files"]}
        self.assertEqual(files["pipeline.py"], "# updated")
        self.assertEqual(files["utils.py"], "# helpers")

    def test_adds_new_file_to_existing_zip(self):
        zip_data = _make_zipfile(("pipeline.py", "# main"))
        pipeline = _make_pipeline_stub(zipfile_data=zip_data)
        result = propose_pipeline_version(
            pipeline,
            [ProposedFile(name="utils.py", content="# new")],
        )
        files = {f["name"]: f["content"] for f in result["files"]}
        self.assertIn("pipeline.py", files)
        self.assertIn("utils.py", files)

    def test_deletes_file_from_existing_zip(self):
        zip_data = _make_zipfile(
            ("pipeline.py", "# main"),
            ("utils.py", "# helpers"),
        )
        pipeline = _make_pipeline_stub(zipfile_data=zip_data)
        result = propose_pipeline_version(
            pipeline,
            modified_files=[],
            deleted_files=["utils.py"],
        )
        files = {f["name"] for f in result["files"]}
        self.assertIn("pipeline.py", files)
        self.assertNotIn("utils.py", files)

    def test_empty_modified_files_returns_existing_files_unchanged(self):
        zip_data = _make_zipfile(("pipeline.py", "# main"))
        pipeline = _make_pipeline_stub(zipfile_data=zip_data)
        result = propose_pipeline_version(pipeline, modified_files=[])
        self.assertEqual(
            result,
            {"files": [{"name": "pipeline.py", "content": "# main"}]},
        )

    def test_no_pipeline_returns_only_modified_files(self):
        result = propose_pipeline_version(
            None,
            [ProposedFile(name="pipeline.py", content="# new")],
        )
        self.assertEqual(
            result,
            {"files": [{"name": "pipeline.py", "content": "# new"}]},
        )
