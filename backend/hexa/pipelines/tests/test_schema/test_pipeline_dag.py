import io
import zipfile

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
        )

        dag = self.query_dag(version)

        self.assertEqual(
            dag["tasks"],
            [
                {"id": "save_dataset", "name": "save_dataset"},
                {"id": "load_history", "name": "load_history"},
                {"id": "load_devices", "name": "load_devices"},
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

        self.assertEqual(self.query_dag(version), {"tasks": [], "edges": []})

    def test_unparseable_zipfile_returns_empty_dag(self):
        """A broken version must degrade to an empty graph, never break the page."""
        version = PipelineVersion.objects.create(
            pipeline=self.PIPELINE,
            user=self.USER_ROOT,
            zipfile=self.build_zipfile({"pipeline.py": "def broken(:\n"}),
        )

        self.assertEqual(self.query_dag(version), {"tasks": [], "edges": []})

    def test_version_without_entrypoint_returns_empty_dag(self):
        version = PipelineVersion.objects.create(
            pipeline=self.PIPELINE,
            user=self.USER_ROOT,
            zipfile=self.build_zipfile({"README.md": "# No code here"}),
        )

        self.assertEqual(self.query_dag(version), {"tasks": [], "edges": []})
