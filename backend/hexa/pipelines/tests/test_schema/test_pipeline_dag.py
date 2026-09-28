import io
import zipfile
from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.pipelines.models import Pipeline, PipelineType, PipelineVersion
from hexa.user_management.models import User
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole
from hexa.workspaces.tests.testutils import create_workspace

PIPELINE_PY = '''from openhexa.sdk import current_run, pipeline, parameter


@pipeline("brussels_bikes", name="Bikes in Brussels")
@parameter("city", name="City", type=str, required=True)
def bikes(city):
    """A diamond: load_devices feeds both consumers, load_history feeds save_dataset."""
    current_run.log_info("Starting pipeline...")
    devices = load_devices(city)
    history = load_history(devices)

    save_dataset(devices, history)


@bikes.task
def save_dataset(devices, history):
    pass


@bikes.task
def load_history(devices):
    pass


@bikes.task
def load_devices(city):
    pass
'''

DAG_QUERY = """
query getPipelineVersion($id: UUID!) {
    pipelineVersion(id: $id) {
        id
        dag {
            tasks { id name }
            edges { source target }
            parameters { code name }
        }
    }
}
"""


class PipelineVersionDagTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_ROOT = User.objects.create_user(
            "root@bluesquarehub.com", "standardpassword", is_superuser=True
        )
        cls.USER_ADMIN = User.objects.create_user(
            "admin@bluesquarehub.com", "standardpassword"
        )
        cls.WORKSPACE = create_workspace(cls.USER_ROOT, name="WS1", description="WS1")
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_ADMIN,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.PIPELINE = Pipeline.objects.create(
            code="pipeline", name="My Pipeline", workspace=cls.WORKSPACE
        )

    def build_zipfile(self, files: dict) -> bytes:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for path, content in files.items():
                zip_file.writestr(path, content)
        return buffer.getvalue()

    def query_dag(self, version: PipelineVersion) -> dict:
        self.client.force_login(self.USER_ADMIN)
        response = self.run_query(DAG_QUERY, {"id": str(version.id)})
        return response["data"]["pipelineVersion"]["dag"]

    def test_resolves_dag_from_zipfile(self):
        version = PipelineVersion.objects.create(
            pipeline=self.PIPELINE,
            user=self.USER_ROOT,
            zipfile=self.build_zipfile({"pipeline.py": PIPELINE_PY}),
            parameters=[{"code": "city", "name": "City", "type": "str"}],
        )

        dag = self.query_dag(version)

        self.assertEqual(
            dag["tasks"],
            [
                {"id": "load_devices", "name": "load_devices"},
                {"id": "load_history", "name": "load_history"},
                {"id": "save_dataset", "name": "save_dataset"},
            ],
        )
        self.assertEqual(
            dag["edges"],
            [
                {"source": "city", "target": "load_devices"},
                {"source": "load_devices", "target": "load_history"},
                {"source": "load_devices", "target": "save_dataset"},
                {"source": "load_history", "target": "save_dataset"},
            ],
        )
        self.assertEqual(dag["parameters"], [{"code": "city", "name": "City"}])

    def test_notebook_version_returns_empty_dag(self):
        """Notebook pipelines carry no archive and must not raise."""
        notebook = Pipeline.objects.create(
            code="notebook-pipeline",
            name="Notebook Pipeline",
            workspace=self.WORKSPACE,
            type=PipelineType.NOTEBOOK,
            notebook_path="analysis.ipynb",
        )
        version = PipelineVersion.objects.create(
            pipeline=notebook, user=self.USER_ROOT, zipfile=None
        )

        self.assertEqual(
            self.query_dag(version), {"tasks": [], "edges": [], "parameters": []}
        )

    def test_unparseable_zipfile_returns_empty_dag(self):
        """A broken version must degrade to an empty graph, never break the page."""
        with self.assertLogs("hexa.pipelines.dag", level="ERROR"):
            version = PipelineVersion.objects.create(
                pipeline=self.PIPELINE,
                user=self.USER_ROOT,
                zipfile=self.build_zipfile({"pipeline.py": "def broken(:\n"}),
            )

        self.assertEqual(
            self.query_dag(version), {"tasks": [], "edges": [], "parameters": []}
        )

    def test_version_without_entrypoint_returns_empty_dag(self):
        version = PipelineVersion.objects.create(
            pipeline=self.PIPELINE,
            user=self.USER_ROOT,
            zipfile=self.build_zipfile({"README.md": "# No code here"}),
        )

        self.assertEqual(
            self.query_dag(version), {"tasks": [], "edges": [], "parameters": []}
        )

    def test_dag_is_stored_when_version_is_created(self):
        version = PipelineVersion.objects.create(
            pipeline=self.PIPELINE,
            user=self.USER_ROOT,
            zipfile=self.build_zipfile({"pipeline.py": PIPELINE_PY}),
        )
        version.refresh_from_db()

        self.assertEqual(len(version.dag["tasks"]), 3)
        with patch("hexa.pipelines.models.extract_dag_from_zipfile") as extract:
            self.assertEqual(self.query_dag(version)["tasks"], version.dag["tasks"])
        extract.assert_not_called()

    def test_version_without_stored_dag_is_filled_on_first_read(self):
        """Versions uploaded before the dag column existed are extracted lazily, once."""
        version = PipelineVersion.objects.create(
            pipeline=self.PIPELINE,
            user=self.USER_ROOT,
            zipfile=self.build_zipfile({"pipeline.py": PIPELINE_PY}),
        )
        PipelineVersion.objects.filter(pk=version.pk).update(dag=None)

        self.assertEqual(len(self.query_dag(version)["tasks"]), 3)
        version.refresh_from_db()
        self.assertEqual(len(version.dag["tasks"]), 3)

    def test_parameter_never_passed_to_a_task_is_left_out(self):
        version = PipelineVersion.objects.create(
            pipeline=self.PIPELINE,
            user=self.USER_ROOT,
            zipfile=self.build_zipfile({"pipeline.py": PIPELINE_PY}),
            parameters=[
                {"code": "unused", "name": "Unused", "type": "int"},
                {"code": "city", "type": "str"},
            ],
        )

        # The unnamed parameter falls back to its code, as everywhere PipelineParameter is used.
        self.assertEqual(
            self.query_dag(version)["parameters"], [{"code": "city", "name": "city"}]
        )

    def test_edge_from_undeclared_parameter_is_dropped(self):
        """``city`` is an argument of the pipeline function but not a declared parameter."""
        version = PipelineVersion.objects.create(
            pipeline=self.PIPELINE,
            user=self.USER_ROOT,
            zipfile=self.build_zipfile({"pipeline.py": PIPELINE_PY}),
            parameters=[],
        )

        dag = self.query_dag(version)

        self.assertNotIn({"source": "city", "target": "load_devices"}, dag["edges"])
        self.assertEqual(len(dag["edges"]), 3)
        self.assertEqual(dag["parameters"], [])
