import base64
import io
import zipfile
from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class PipelineVersionsTest(GraphQLTestCase):
    USER_ROOT = None
    USER_ADMIN = None
    WORKSPACE = None
    PIPELINE = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_ROOT = User.objects.create_user(
            "root@bluesquarehub.com",
            "standardpassword",
            is_superuser=True,
        )
        cls.USER_ADMIN = User.objects.create_user(
            "noob@bluesquarehub.com",
            "standardpassword",
        )
        cls.USER_LAMBDA = User.objects.create_user(
            "viewer@bluesquarehub.com",
            "standardpassword",
        )
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )

        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            cls.WORKSPACE = Workspace.objects.create_if_has_perm(
                cls.USER_ROOT,
                name="WS1",
                description="Workspace 1",
            )
        cls.WORKSPACE_MEMBERSHIP_1 = WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_ADMIN,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.WORKSPACE_MEMBERSHIP_2 = WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_SABRINA,
            role=WorkspaceMembershipRole.VIEWER,
        )

        cls.PIPELINE = Pipeline.objects.create(
            code="pipeline", name="My Pipeline", workspace=cls.WORKSPACE
        )
        cls.pipeline_py_content = '''from openhexa.sdk import pipeline, parameter

@pipeline(name="Test Data Pipeline")
@parameter("file_path", name="File Path", type=str, required=True)
def test_pipeline(input_file, threshold, enable_debug):
    """Process data from input file."""
    pass
'''

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("pipeline.py", cls.pipeline_py_content)
        cls.zip_pipeline_py = base64.b64encode(zip_buffer.getvalue()).decode("ascii")

    def create_version(self, version, user=None, zip_file=None):
        user = user or self.USER_ADMIN
        self.client.force_login(user)
        return self.run_query(
            """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                    details
                }
            }
            """,
            {
                "input": {
                    "code": self.PIPELINE.code,
                    "workspaceSlug": self.WORKSPACE.slug,
                    "name": version,
                    "zipfile": zip_file or self.zip_pipeline_py,
                }
            },
        )

    def test_create_version(self, version="First Version", user=None, zip_file=None):
        r = self.create_version(version, user, zip_file)
        self.assertEqual(r["data"]["uploadPipeline"]["success"], True)

    def test_duplicate_versions(self):
        name = "Version 1"
        self.create_version(name)
        r = self.create_version(name)
        self.assertEqual(r["data"]["uploadPipeline"]["success"], False)
        self.assertEqual(
            r["data"]["uploadPipeline"]["errors"], ["DUPLICATE_PIPELINE_VERSION_NAME"]
        )

    def test_version_is_latest(self):
        self.test_create_version("Version 1")
        self.test_create_version("Version 2")
        self.test_create_version("Version 3")

        self.assertTrue(self.PIPELINE.last_version.is_latest_version)
        self.assertFalse(self.PIPELINE.versions.last().is_latest_version)

    def test_update_version(self):
        self.test_create_version("Version 1")

        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            mutation updatePipelineVersion($input: UpdatePipelineVersionInput!) {
                updatePipelineVersion(input: $input) {
                    success
                    errors
                    pipelineVersion {
                        id
                        name
                        externalLink
                        description
                        config
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.PIPELINE.last_version.id),
                    "name": "New Version Name",
                    "externalLink": "https://example.com",
                    "description": "New Description",
                    "config": {"dhis2_connection": "abcd"},
                }
            },
        )

        self.assertEqual(
            r["data"]["updatePipelineVersion"],
            {
                "success": True,
                "errors": [],
                "pipelineVersion": {
                    "id": str(self.PIPELINE.last_version.id),
                    "name": "New Version Name",
                    "externalLink": "https://example.com",
                    "description": "New Description",
                    "config": {"dhis2_connection": "abcd"},
                },
            },
        )

    def test_create_version_with_unschedulable_config(self):
        self.test_create_version_with_parameters(version="Version 2 with parameters")

        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            mutation updatePipelineVersion($input: UpdatePipelineVersionInput!) {
                updatePipelineVersion(input: $input) {
                    success
                    errors
                    pipelineVersion {
                        id
                        name
                        externalLink
                        description
                        config
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.PIPELINE.last_version.id),
                    "name": "New Version Name",
                    "externalLink": "https://example.com",
                    "description": "New Description",
                    "config": {"param_example": "example_value"},
                }
            },
        )
        self.assertEqual(
            r["data"]["updatePipelineVersion"],
            {
                "success": True,
                "errors": [],
                "pipelineVersion": {
                    "id": str(self.PIPELINE.last_version.id),
                    "name": "New Version Name",
                    "externalLink": "https://example.com",
                    "description": "New Description",
                    "config": {"param_example": "example_value"},
                },
            },
        )

        r = self.run_query(
            """
            mutation updatePipelineVersion($input: UpdatePipelineVersionInput!) {
                updatePipelineVersion(input: $input) {
                    success
                    errors
                    pipelineVersion {
                        id
                        name
                        externalLink
                        description
                        config
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.PIPELINE.last_version.id),
                    "name": "New Version Name",
                    "externalLink": "https://example.com",
                    "description": "New Description",
                    "config": {"param_example": None},
                }
            },
        )
        self.assertEqual(
            "Cannot push an unschedulable new version for a scheduled pipeline.",
            r["errors"][0]["message"],
        )

    def test_create_version_not_admin(self):
        self.client.force_login(self.USER_SABRINA)

        r = self.run_query(
            """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "code": self.PIPELINE.code,
                    "workspaceSlug": self.WORKSPACE.slug,
                    "name": "version",
                    "zipfile": self.zip_pipeline_py,
                }
            },
        )
        self.assertEqual(
            r["data"]["uploadPipeline"],
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            },
        )

    def test_update_version_not_admin(self):
        self.test_create_version("Version 1", user=self.USER_ADMIN)

        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation updatePipelineVersion($input: UpdatePipelineVersionInput!) {
                updatePipelineVersion(input: $input) {
                    success
                    errors
                    pipelineVersion {
                        id
                        name
                        externalLink
                        description

                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.PIPELINE.last_version.id),
                    "name": "New Version Name",
                    "externalLink": "https://example.com",
                    "description": "New Description",
                }
            },
        )

        self.assertEqual(
            r["data"]["updatePipelineVersion"],
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
                "pipelineVersion": None,
            },
        )

    def test_create_version_with_parameters(self, version="Filler", user=None):
        if user is None:
            user = self.USER_ADMIN
        self.client.force_login(user)

        r = self.run_query(
            """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "code": self.PIPELINE.code,
                    "workspaceSlug": self.WORKSPACE.slug,
                    "name": version,
                    "parameters": [
                        {
                            "code": "param_example",
                            "name": "Param Example",
                            "type": "str",
                            "help": "Param Example's Help",
                            "default": None,
                            "multiple": False,
                            "required": True,
                            "choices": [],
                        }
                    ],
                    "zipfile": "",
                }
            },
        )
        pipeline = Pipeline.objects.filter_for_user(self.USER_ROOT).first()
        pipeline.schedule = "0 15 * * *"
        pipeline.save()
        self.assertEqual(r["data"]["uploadPipeline"]["success"], True)

    def test_increment_version_number_on_save(self):
        self.test_create_version("First version")
        self.test_create_version("Second version")
        self.create_version(None)

        pipeline = Pipeline.objects.filter(code=self.PIPELINE.code).first()

        first_version = pipeline.versions.filter(name="First version").first()
        self.assertEqual(first_version.version_number, 1)
        self.assertEqual(first_version.version_name, "First version [v1]")
        self.assertEqual(first_version.display_name, "My Pipeline - First version [v1]")

        self.assertEqual(
            pipeline.versions.filter(name="Second version").first().version_number, 2
        )

        third_version = pipeline.versions.filter(name__isnull=True).first()
        self.assertEqual(third_version.version_number, 3)
        self.assertEqual(third_version.version_name, "v3")
        self.assertEqual(third_version.display_name, "My Pipeline - v3")

    def create_version_with_files(self, version_name="Version with files"):
        """Helper method to create a pipeline version with actual files in the ZIP."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("main1.py", "print('Hello World')\n")
            zip_file.writestr(
                "pipeline.py", "def run_pipeline():\n    print('Running pipeline')\n"
            )
            zip_file.writestr("requirements.txt", "pandas==1.5.0\nnumpy==1.21.0\n")
            zip_file.writestr("utils/", "")
            zip_file.writestr(
                "utils/helpers.py", "def helper_function():\n    return 'helper'\n"
            )
            zip_file.writestr(
                "README.md", "# Test Pipeline\n\nThis is a test pipeline.\n"
            )

        zip_buffer.seek(0)
        zipfile_b64 = base64.b64encode(zip_buffer.getvalue()).decode("ascii")

        self.client.force_login(self.USER_ADMIN)
        return self.run_query(
            """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                    pipelineVersion {
                        id
                        name
                    }
                }
            }
            """,
            {
                "input": {
                    "code": self.PIPELINE.code,
                    "workspaceSlug": self.WORKSPACE.slug,
                    "name": version_name,
                    "parameters": [],
                    "zipfile": zipfile_b64,
                }
            },
        )

    def test_pipeline_version_files_resolver(self):
        """Test that the files resolver correctly extracts and returns flattened files from the ZIP."""
        create_response = self.create_version_with_files()
        self.assertTrue(create_response["data"]["uploadPipeline"]["success"])

        version_id = create_response["data"]["uploadPipeline"]["pipelineVersion"]["id"]

        self.client.force_login(self.USER_ADMIN)
        response = self.run_query(
            """
            query getPipelineVersion($id: UUID!) {
                pipelineVersion(id: $id) {
                    id
                    name
                    files {
                        id
                        name
                        path
                        type
                        content
                        parentId
                        autoSelect
                    }
                }
            }
            """,
            {"id": version_id},
        )

        self.assertIsNotNone(response["data"]["pipelineVersion"])
        files = response["data"]["pipelineVersion"]["files"]

        self.assertEqual(len(files), 6)  # 5 files + 1 utils directory

        main_py = next((f for f in files if f["name"] == "main1.py"), None)
        self.assertIsNotNone(main_py)
        self.assertEqual(main_py["id"], "Version with files [v1]/main1.py")
        self.assertEqual(main_py["path"], "main1.py")
        self.assertEqual(main_py["type"], "file")
        self.assertEqual(main_py["parentId"], None)
        self.assertFalse(main_py["autoSelect"])
        self.assertEqual(main_py["content"], "print('Hello World')\n")

        pipeline_py = next((f for f in files if f["name"] == "pipeline.py"), None)
        self.assertIsNotNone(pipeline_py)
        self.assertEqual(pipeline_py["id"], "Version with files [v1]/pipeline.py")
        self.assertEqual(pipeline_py["path"], "pipeline.py")
        self.assertEqual(pipeline_py["type"], "file")
        self.assertEqual(pipeline_py["parentId"], None)
        self.assertTrue(pipeline_py["autoSelect"])
        self.assertEqual(
            pipeline_py["content"],
            "def run_pipeline():\n    print('Running pipeline')\n",
        )

        requirements_txt = next(
            (f for f in files if f["name"] == "requirements.txt"), None
        )
        self.assertIsNotNone(requirements_txt)
        self.assertEqual(
            requirements_txt["id"], "Version with files [v1]/requirements.txt"
        )
        self.assertEqual(requirements_txt["type"], "file")
        self.assertEqual(requirements_txt["parentId"], None)
        self.assertFalse(requirements_txt["autoSelect"])
        self.assertEqual(requirements_txt["content"], "pandas==1.5.0\nnumpy==1.21.0\n")

        utils_dir = next((f for f in files if f["name"] == "utils"), None)
        self.assertIsNotNone(utils_dir)
        self.assertEqual(utils_dir["id"], "Version with files [v1]/utils")
        self.assertEqual(utils_dir["path"], "utils")
        self.assertEqual(utils_dir["type"], "directory")
        self.assertEqual(utils_dir["parentId"], None)
        self.assertIsNone(utils_dir["content"])
        self.assertFalse(utils_dir["autoSelect"])

        helpers_py = next((f for f in files if f["name"] == "helpers.py"), None)
        self.assertIsNotNone(helpers_py)
        self.assertEqual(helpers_py["id"], "Version with files [v1]/utils/helpers.py")
        self.assertEqual(helpers_py["path"], "utils/helpers.py")
        self.assertEqual(helpers_py["type"], "file")
        self.assertEqual(helpers_py["parentId"], "Version with files [v1]/utils")
        self.assertFalse(helpers_py["autoSelect"])
        self.assertEqual(
            helpers_py["content"], "def helper_function():\n    return 'helper'\n"
        )

        readme = next((f for f in files if f["name"] == "README.md"), None)
        self.assertIsNotNone(readme)
        self.assertEqual(readme["id"], "Version with files [v1]/README.md")
        self.assertEqual(readme["type"], "file")
        self.assertEqual(readme["parentId"], None)  # Root file
        self.assertFalse(readme["autoSelect"])
        self.assertEqual(
            readme["content"], "# Test Pipeline\n\nThis is a test pipeline.\n"
        )

    def test_pipeline_version_files_empty_zipfile(self):
        """Test that the files resolver handles empty zipfiles gracefully."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED):
            pass
        empty_zip_b64 = base64.b64encode(zip_buffer.getvalue()).decode("ascii")
        self.test_create_version("Empty Version", zip_file=empty_zip_b64)

        version_id = str(self.PIPELINE.last_version.id)

        self.client.force_login(self.USER_ADMIN)
        response = self.run_query(
            """
            query getPipelineVersion($id: UUID!) {
                pipelineVersion(id: $id) {
                    id
                    files {
                        name
                        path
                        type
                        content
                    }
                }
            }
            """,
            {"id": version_id},
        )

        self.assertEqual(response["data"]["pipelineVersion"]["files"], [])

    def _create_version_with_typed_params(self):
        return PipelineVersion.objects.create(
            pipeline=self.PIPELINE,
            parameters=[
                {
                    "code": "count",
                    "name": "Count",
                    "type": "int",
                    "multiple": False,
                    "required": False,
                    "choices": [],
                },
                {
                    "code": "score",
                    "name": "Score",
                    "type": "float",
                    "multiple": False,
                    "required": False,
                    "choices": [],
                },
                {
                    "code": "label",
                    "name": "Label",
                    "type": "str",
                    "multiple": False,
                    "required": False,
                    "choices": [],
                },
                {
                    "code": "flag",
                    "name": "Flag",
                    "type": "bool",
                    "multiple": False,
                    "required": False,
                    "choices": [],
                },
                {
                    "code": "conn",
                    "name": "Conn",
                    "type": "dhis2",
                    "multiple": False,
                    "required": False,
                    "choices": [],
                },
            ],
        )

    def test_update_version_config_invalid_types(self):
        version = self._create_version_with_typed_params()
        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            mutation updatePipelineVersion($input: UpdatePipelineVersionInput!) {
                updatePipelineVersion(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"id": str(version.id), "config": {"count": "not_a_number"}}},
        )
        self.assertEqual(r["data"]["updatePipelineVersion"]["success"], False)
        self.assertIn("INVALID_CONFIG", r["data"]["updatePipelineVersion"]["errors"])

    def test_update_version_config_valid_types(self):
        version = self._create_version_with_typed_params()
        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            mutation updatePipelineVersion($input: UpdatePipelineVersionInput!) {
                updatePipelineVersion(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(version.id),
                    "config": {
                        "count": 5,
                        "score": 3.14,
                        "label": "hello",
                        "flag": True,
                        "conn": "some-connection-id",
                    },
                }
            },
        )
        self.assertEqual(r["data"]["updatePipelineVersion"]["success"], True)
        self.assertEqual(r["data"]["updatePipelineVersion"]["errors"], [])


class UploadPipelineFilesInputTest(GraphQLTestCase):
    """Tests for UploadPipelineInput.files — the alternative to a base64 zipfile."""

    PIPELINE_PY = (
        "from openhexa.sdk import pipeline\n\n"
        '@pipeline("test")\n'
        "def test_pipeline():\n"
        "    pass\n"
    )

    @classmethod
    def setUpTestData(cls):
        cls.USER_ROOT = User.objects.create_user(
            "root-files@bluesquarehub.com",
            "standardpassword",
            is_superuser=True,
        )
        cls.USER_ADMIN = User.objects.create_user(
            "admin-files@bluesquarehub.com",
            "standardpassword",
        )
        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            cls.WORKSPACE = Workspace.objects.create_if_has_perm(
                cls.USER_ROOT,
                name="WS Files",
                description="Files-input workspace",
            )
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_ADMIN,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.PIPELINE = Pipeline.objects.create(
            code="pipeline-files", name="Files Pipeline", workspace=cls.WORKSPACE
        )

    def _upload(self, **input_overrides):
        self.client.force_login(self.USER_ADMIN)
        return self.run_query(
            """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                    details
                    pipelineVersion { id versionNumber }
                }
            }
            """,
            {
                "input": {
                    "workspaceSlug": self.WORKSPACE.slug,
                    "pipelineCode": self.PIPELINE.code,
                    **input_overrides,
                }
            },
        )

    def _zip_contents(self, version: PipelineVersion) -> dict[str, bytes]:
        with zipfile.ZipFile(io.BytesIO(version.zipfile)) as zf:
            return {name: zf.read(name) for name in zf.namelist()}

    def test_upload_with_files_builds_zip(self):
        files = [
            {"path": "pipeline.py", "content": self.PIPELINE_PY},
            {"path": "lib/helpers.py", "content": "def clean(df):\n    return df\n"},
            {"path": "requirements.txt", "content": "pandas\n"},
        ]
        r = self._upload(name="v-files", files=files)
        self.assertTrue(r["data"]["uploadPipeline"]["success"], r["data"])

        version = PipelineVersion.objects.get(
            id=r["data"]["uploadPipeline"]["pipelineVersion"]["id"]
        )
        contents = self._zip_contents(version)
        self.assertEqual(
            set(contents), {"pipeline.py", "lib/helpers.py", "requirements.txt"}
        )
        self.assertEqual(contents["requirements.txt"], b"pandas\n")

    def test_upload_with_base64_file(self):
        binary_payload = b"\x89PNG\r\n\x1a\n\x00"
        files = [
            {"path": "pipeline.py", "content": self.PIPELINE_PY},
            {
                "path": "assets/logo.png",
                "content": base64.b64encode(binary_payload).decode("ascii"),
                "encoding": "BASE64",
            },
        ]
        r = self._upload(name="v-b64", files=files)
        self.assertTrue(r["data"]["uploadPipeline"]["success"], r["data"])

        version = PipelineVersion.objects.get(
            id=r["data"]["uploadPipeline"]["pipelineVersion"]["id"]
        )
        self.assertEqual(self._zip_contents(version)["assets/logo.png"], binary_payload)

    def test_upload_rejects_both_zipfile_and_files(self):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            zf.writestr("pipeline.py", self.PIPELINE_PY)
        zip_b64 = base64.b64encode(zip_buffer.getvalue()).decode("ascii")

        r = self._upload(
            name="v-both",
            zipfile=zip_b64,
            files=[{"path": "pipeline.py", "content": self.PIPELINE_PY}],
        )
        self.assertFalse(r["data"]["uploadPipeline"]["success"])
        self.assertEqual(
            r["data"]["uploadPipeline"]["errors"], ["INVALID_VERSION_FILES"]
        )

    def test_upload_rejects_neither_zipfile_nor_files(self):
        r = self._upload(name="v-neither")
        self.assertFalse(r["data"]["uploadPipeline"]["success"])
        self.assertEqual(
            r["data"]["uploadPipeline"]["errors"], ["INVALID_VERSION_FILES"]
        )

    def test_upload_rejects_duplicate_paths(self):
        files = [
            {"path": "pipeline.py", "content": self.PIPELINE_PY},
            {"path": "pipeline.py", "content": "x = 1\n"},
        ]
        r = self._upload(name="v-dup", files=files)
        self.assertFalse(r["data"]["uploadPipeline"]["success"])
        self.assertEqual(
            r["data"]["uploadPipeline"]["errors"], ["INVALID_VERSION_FILES"]
        )
        self.assertIn("duplicate", r["data"]["uploadPipeline"]["details"].lower())

    def test_upload_missing_pipeline_py_is_not_enforced(self):
        files = [{"path": "helpers.py", "content": "x = 1\n"}]
        r = self._upload(name="v-nopipeline", files=files)
        self.assertTrue(r["data"]["uploadPipeline"]["success"], r["data"])
        version = PipelineVersion.objects.get(
            id=r["data"]["uploadPipeline"]["pipelineVersion"]["id"]
        )
        self.assertEqual(version.parameters, [])
