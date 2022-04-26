from urllib.parse import urljoin

import responses

from hexa.core.test import TestCase
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    AnalysisStatus,
    Project,
)
from hexa.plugins.connector_airflow.models import DAG, Cluster, DAGRunState, DAGTemplate
from hexa.user_management.models import User


class AccessmodSignalsTest(TestCase):
    @classmethod
    @responses.activate
    def setUpTestData(cls):
        cls.USER_MARLA = User.objects.create_user(
            "marla@bluesquarehub.com",
            "marla-secure-password",
        )
        cls.CLUSTER = Cluster.objects.create(
            name="Marla's cluster", url="https://marla-cluster-url.com"
        )
        cls.TEMPLATE = DAGTemplate.objects.create(cluster=cls.CLUSTER, code="MAGIC")
        cls.DAG = DAG.objects.create(template=cls.TEMPLATE, dag_id="magic_dag")

        responses.add(
            responses.POST,
            urljoin(cls.CLUSTER.api_url, f"dags/{cls.DAG.dag_id}/dagRuns"),
            json={
                "conf": {},
                "magic_dag": "test_dag",
                "dag_run_id": "magic_dag_run_1",
                "end_date": "2021-10-09T16:42:16.189200+00:00",
                "execution_date": "2021-10-09T16:41:00+00:00",
                "external_trigger": False,
                "start_date": "2021-10-09T16:42:00.830209+00:00",
                "state": "queued",
            },
            status=200,
        )

        cls.DAG_RUN = cls.DAG.run(
            request=cls.mock_request(cls.USER_MARLA),
        )
        cls.SAMPLE_PROJECT = Project.objects.create(
            name="Marla's first project",
            country="BE",
            author=cls.USER_MARLA,
            spatial_resolution=100,
            crs=4326,
        )
        cls.ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            author=cls.USER_MARLA,
            project=cls.SAMPLE_PROJECT,
            name="Test accessibility analysis",
            dag_run=cls.DAG_RUN,
            status=AnalysisStatus.QUEUED,
        )

    def test_queued(self):
        self.DAG_RUN.state = DAGRunState.QUEUED
        self.DAG_RUN.save()
        self.ACCESSIBILITY_ANALYSIS.refresh_from_db()
        self.assertEqual(AnalysisStatus.QUEUED, self.ACCESSIBILITY_ANALYSIS.status)

    def test_running(self):
        self.DAG_RUN.state = DAGRunState.RUNNING
        self.DAG_RUN.save()
        self.ACCESSIBILITY_ANALYSIS.refresh_from_db()
        self.assertEqual(AnalysisStatus.RUNNING, self.ACCESSIBILITY_ANALYSIS.status)

    def test_success(self):
        self.DAG_RUN.state = DAGRunState.SUCCESS
        self.DAG_RUN.save()
        self.ACCESSIBILITY_ANALYSIS.refresh_from_db()
        self.assertEqual(AnalysisStatus.SUCCESS, self.ACCESSIBILITY_ANALYSIS.status)

    def test_failed(self):
        self.DAG_RUN.state = DAGRunState.FAILED
        self.DAG_RUN.save()
        self.ACCESSIBILITY_ANALYSIS.refresh_from_db()
        self.assertEqual(AnalysisStatus.FAILED, self.ACCESSIBILITY_ANALYSIS.status)
