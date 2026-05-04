"""Tests for the pipelineParameterChoices query resolver."""

from unittest.mock import MagicMock, patch

from hexa.core.test import GraphQLTestCase
from hexa.files.backends.exceptions import NotFound
from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)

QUERY = """
    query pipelineParameterChoices(
        $workspaceSlug: String!
        $pipelineVersionId: UUID!
        $parameterCode: String!
    ) {
        pipelineParameterChoices(
            workspaceSlug: $workspaceSlug
            pipelineVersionId: $pipelineVersionId
            parameterCode: $parameterCode
        )
    }
"""

_CSV_SINGLE_COL = b"district\nNairobi\nMombasa\nKisumu\n"
_CSV_MULTI_COL = b"code,name\nNBI,Nairobi\nMSA,Mombasa\n"
_JSON_FLAT = b'["Nairobi", "Mombasa", "Kisumu"]'
_JSON_OBJECTS = (
    b'[{"code": "NBI", "name": "Nairobi"}, {"code": "MSA", "name": "Mombasa"}]'
)
_YAML_FLAT = b"- Nairobi\n- Mombasa\n- Kisumu\n"
_YAML_OBJECTS = b"- code: NBI\n  name: Nairobi\n- code: MSA\n  name: Mombasa\n"


def _make_storage_object(size=100):
    obj = MagicMock()
    obj.size = size
    obj.type = "file"
    return obj


class PipelineParameterChoicesTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "member@example.com", "password", is_superuser=True
        )
        cls.OUTSIDER = User.objects.create_user("outsider@example.com", "password")

        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            cls.WORKSPACE = Workspace.objects.create_if_has_perm(
                cls.USER,
                name="Test Workspace",
                description="",
            )

        WorkspaceMembership.objects.get_or_create(
            workspace=cls.WORKSPACE,
            user=cls.USER,
            defaults={"role": WorkspaceMembershipRole.EDITOR},
        )

        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="Test Pipeline",
            code="test-pipeline",
        )

    def _create_version(self, parameters):
        return PipelineVersion.objects.create(
            pipeline=self.PIPELINE,
            user=self.USER,
            parameters=parameters,
            version_number=PipelineVersion.objects.filter(
                pipeline=self.PIPELINE
            ).count()
            + 1,
        )

    def _run(self, version, code):
        self.client.force_login(self.USER)
        return self.run_query(
            QUERY,
            {
                "workspaceSlug": self.WORKSPACE.slug,
                "pipelineVersionId": str(version.id),
                "parameterCode": code,
            },
        )

    # ------------------------------------------------------------------
    # CSV
    # ------------------------------------------------------------------

    def test_csv_single_column(self):
        version = self._create_version(
            [
                {
                    "code": "district",
                    "type": "str",
                    "choices_from_file": {
                        "format": "csv",
                        "path": "districts.csv",
                        "column": None,
                    },
                }
            ]
        )
        with (
            patch(
                "hexa.pipelines.choices_from_file.storage.get_bucket_object",
                return_value=_make_storage_object(),
            ),
            patch(
                "hexa.pipelines.choices_from_file.storage.read_object",
                return_value=_CSV_SINGLE_COL,
            ),
        ):
            r = self._run(version, "district")
        self.assertEqual(
            r["data"]["pipelineParameterChoices"], ["Nairobi", "Mombasa", "Kisumu"]
        )

    def test_csv_multi_column_with_column_specified(self):
        version = self._create_version(
            [
                {
                    "code": "district",
                    "type": "str",
                    "choices_from_file": {
                        "format": "csv",
                        "path": "districts.csv",
                        "column": "code",
                    },
                }
            ]
        )
        with (
            patch(
                "hexa.pipelines.choices_from_file.storage.get_bucket_object",
                return_value=_make_storage_object(),
            ),
            patch(
                "hexa.pipelines.choices_from_file.storage.read_object",
                return_value=_CSV_MULTI_COL,
            ),
        ):
            r = self._run(version, "district")
        self.assertEqual(r["data"]["pipelineParameterChoices"], ["NBI", "MSA"])

    def test_csv_multi_column_no_column_raises(self):
        version = self._create_version(
            [
                {
                    "code": "district",
                    "type": "str",
                    "choices_from_file": {
                        "format": "csv",
                        "path": "districts.csv",
                        "column": None,
                    },
                }
            ]
        )
        with (
            patch(
                "hexa.pipelines.choices_from_file.storage.get_bucket_object",
                return_value=_make_storage_object(),
            ),
            patch(
                "hexa.pipelines.choices_from_file.storage.read_object",
                return_value=_CSV_MULTI_COL,
            ),
        ):
            r = self._run(version, "district")
        self.assertIsNone(r["data"]["pipelineParameterChoices"])
        self.assertTrue(any("multiple columns" in str(e) for e in r["errors"]))

    def test_csv_missing_column_raises(self):
        version = self._create_version(
            [
                {
                    "code": "district",
                    "type": "str",
                    "choices_from_file": {
                        "format": "csv",
                        "path": "districts.csv",
                        "column": "nonexistent",
                    },
                }
            ]
        )
        with (
            patch(
                "hexa.pipelines.choices_from_file.storage.get_bucket_object",
                return_value=_make_storage_object(),
            ),
            patch(
                "hexa.pipelines.choices_from_file.storage.read_object",
                return_value=_CSV_SINGLE_COL,
            ),
        ):
            r = self._run(version, "district")
        self.assertIsNone(r["data"]["pipelineParameterChoices"])
        self.assertTrue(any("not found" in str(e).lower() for e in r["errors"]))

    # ------------------------------------------------------------------
    # JSON
    # ------------------------------------------------------------------

    def test_json_flat_array(self):
        version = self._create_version(
            [
                {
                    "code": "district",
                    "type": "str",
                    "choices_from_file": {
                        "format": "json",
                        "path": "regions.json",
                        "column": None,
                    },
                }
            ]
        )
        with (
            patch(
                "hexa.pipelines.choices_from_file.storage.get_bucket_object",
                return_value=_make_storage_object(),
            ),
            patch(
                "hexa.pipelines.choices_from_file.storage.read_object",
                return_value=_JSON_FLAT,
            ),
        ):
            r = self._run(version, "district")
        self.assertEqual(
            r["data"]["pipelineParameterChoices"], ["Nairobi", "Mombasa", "Kisumu"]
        )

    def test_json_objects_with_column(self):
        version = self._create_version(
            [
                {
                    "code": "district",
                    "type": "str",
                    "choices_from_file": {
                        "format": "json",
                        "path": "regions.json",
                        "column": "code",
                    },
                }
            ]
        )
        with (
            patch(
                "hexa.pipelines.choices_from_file.storage.get_bucket_object",
                return_value=_make_storage_object(),
            ),
            patch(
                "hexa.pipelines.choices_from_file.storage.read_object",
                return_value=_JSON_OBJECTS,
            ),
        ):
            r = self._run(version, "district")
        self.assertEqual(r["data"]["pipelineParameterChoices"], ["NBI", "MSA"])

    def test_json_objects_no_column_raises(self):
        version = self._create_version(
            [
                {
                    "code": "district",
                    "type": "str",
                    "choices_from_file": {
                        "format": "json",
                        "path": "regions.json",
                        "column": None,
                    },
                }
            ]
        )
        with (
            patch(
                "hexa.pipelines.choices_from_file.storage.get_bucket_object",
                return_value=_make_storage_object(),
            ),
            patch(
                "hexa.pipelines.choices_from_file.storage.read_object",
                return_value=_JSON_OBJECTS,
            ),
        ):
            r = self._run(version, "district")
        self.assertIsNone(r["data"]["pipelineParameterChoices"])
        self.assertTrue(any("multiple keys" in str(e) for e in r["errors"]))

    # ------------------------------------------------------------------
    # YAML
    # ------------------------------------------------------------------

    def test_yaml_flat_sequence(self):
        version = self._create_version(
            [
                {
                    "code": "district",
                    "type": "str",
                    "choices_from_file": {
                        "format": "yaml",
                        "path": "list.yaml",
                        "column": None,
                    },
                }
            ]
        )
        with (
            patch(
                "hexa.pipelines.choices_from_file.storage.get_bucket_object",
                return_value=_make_storage_object(),
            ),
            patch(
                "hexa.pipelines.choices_from_file.storage.read_object",
                return_value=_YAML_FLAT,
            ),
        ):
            r = self._run(version, "district")
        self.assertEqual(
            r["data"]["pipelineParameterChoices"], ["Nairobi", "Mombasa", "Kisumu"]
        )

    def test_yaml_objects_with_column(self):
        version = self._create_version(
            [
                {
                    "code": "district",
                    "type": "str",
                    "choices_from_file": {
                        "format": "yaml",
                        "path": "list.yaml",
                        "column": "code",
                    },
                }
            ]
        )
        with (
            patch(
                "hexa.pipelines.choices_from_file.storage.get_bucket_object",
                return_value=_make_storage_object(),
            ),
            patch(
                "hexa.pipelines.choices_from_file.storage.read_object",
                return_value=_YAML_OBJECTS,
            ),
        ):
            r = self._run(version, "district")
        self.assertEqual(r["data"]["pipelineParameterChoices"], ["NBI", "MSA"])

    # ------------------------------------------------------------------
    # Error cases
    # ------------------------------------------------------------------

    def test_file_not_found(self):
        version = self._create_version(
            [
                {
                    "code": "district",
                    "type": "str",
                    "choices_from_file": {
                        "format": "csv",
                        "path": "missing.csv",
                        "column": None,
                    },
                }
            ]
        )
        with patch(
            "hexa.pipelines.choices_from_file.storage.get_bucket_object",
            side_effect=NotFound("not found"),
        ):
            r = self._run(version, "district")
        self.assertIsNone(r["data"]["pipelineParameterChoices"])
        self.assertTrue(any("not found" in str(e).lower() for e in r["errors"]))

    def test_parameter_has_no_file_choices(self):
        version = self._create_version(
            [{"code": "country", "type": "str", "choices": ["UG", "KE"]}]
        )
        r = self._run(version, "country")
        self.assertIsNone(r["data"]["pipelineParameterChoices"])
        self.assertTrue(
            any("does not have dynamic choices" in str(e) for e in r["errors"])
        )

    def test_parameter_code_not_found(self):
        version = self._create_version(
            [
                {
                    "code": "district",
                    "type": "str",
                    "choices_from_file": {
                        "format": "csv",
                        "path": "d.csv",
                        "column": None,
                    },
                }
            ]
        )
        r = self._run(version, "nonexistent")
        self.assertIsNone(r["data"]["pipelineParameterChoices"])
        self.assertTrue(any("not found" in str(e).lower() for e in r["errors"]))

    def test_workspace_not_found(self):
        version = self._create_version(
            [
                {
                    "code": "district",
                    "type": "str",
                    "choices_from_file": {
                        "format": "csv",
                        "path": "d.csv",
                        "column": None,
                    },
                }
            ]
        )
        self.client.force_login(self.USER)
        r = self.run_query(
            QUERY,
            {
                "workspaceSlug": "nonexistent-slug",
                "pipelineVersionId": str(version.id),
                "parameterCode": "district",
            },
        )
        self.assertIsNone(r["data"]["pipelineParameterChoices"])

    def test_outsider_cannot_access(self):
        version = self._create_version(
            [
                {
                    "code": "district",
                    "type": "str",
                    "choices_from_file": {
                        "format": "csv",
                        "path": "d.csv",
                        "column": None,
                    },
                }
            ]
        )
        self.client.force_login(self.OUTSIDER)
        r = self.run_query(
            QUERY,
            {
                "workspaceSlug": self.WORKSPACE.slug,
                "pipelineVersionId": str(version.id),
                "parameterCode": "district",
            },
        )
        self.assertIsNone(r["data"]["pipelineParameterChoices"])

    def test_file_too_large(self):
        version = self._create_version(
            [
                {
                    "code": "district",
                    "type": "str",
                    "choices_from_file": {
                        "format": "csv",
                        "path": "huge.csv",
                        "column": None,
                    },
                }
            ]
        )
        with patch(
            "hexa.pipelines.choices_from_file.storage.get_bucket_object",
            return_value=_make_storage_object(size=10 * 1024 * 1024),
        ):
            r = self._run(version, "district")
        self.assertIsNone(r["data"]["pipelineParameterChoices"])
        self.assertTrue(any("too large" in str(e).lower() for e in r["errors"]))
