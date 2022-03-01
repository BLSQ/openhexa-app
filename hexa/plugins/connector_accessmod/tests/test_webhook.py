import uuid
from base64 import b64encode
from datetime import datetime
from urllib.parse import urljoin

import responses
from django.core.signing import Signer
from django.urls import reverse
from django.utils import timezone

from hexa.core.test import TestCase
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    AnalysisStatus,
    Fileset,
    FilesetFormat,
    FilesetRole,
    FilesetRoleCode,
    Project,
)
from hexa.plugins.connector_airflow.models import DAG, Cluster, DAGTemplate
from hexa.user_management.models import User


class AccessmodViewsTest(TestCase):
    @classmethod
    @responses.activate
    def setUpTestData(cls):
        cls.USER_TAYLOR = User.objects.create_user(
            "taylor@bluesquarehub.com",
            "taylorrocks66",
            is_superuser=True,
        )
        cls.CLUSTER = Cluster.objects.create(
            name="Test cluster", url="https://one-cluster-url.com"
        )
        cls.TEMPLATE = DAGTemplate.objects.create(cluster=cls.CLUSTER, code="TEST")
        cls.DAG = DAG.objects.create(template=cls.TEMPLATE, dag_id="test_dag")

        responses.add(
            responses.POST,
            urljoin(cls.CLUSTER.api_url, f"dags/{cls.DAG.dag_id}/dagRuns"),
            json={
                "conf": {},
                "dag_id": "test_dag",
                "dag_run_id": "test_dag_run_1",
                "end_date": "2021-10-09T16:42:16.189200+00:00",
                "execution_date": "2021-10-09T16:41:00+00:00",
                "external_trigger": False,
                "start_date": "2021-10-09T16:42:00.830209+00:00",
                "state": "queued",
            },
            status=200,
        )
        cls.DAG_RUN = cls.DAG.run(
            request=cls.mock_request(cls.USER_TAYLOR),
            webhook_path=reverse("connector_accessmod:webhook"),
        )
        cls.SAMPLE_PROJECT = Project.objects.create(
            name="Sample project",
            country="BE",
            owner=cls.USER_TAYLOR,
            spatial_resolution=100,
            crs=4326,
        )
        cls.ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            owner=cls.USER_TAYLOR,
            project=cls.SAMPLE_PROJECT,
            name="Test accessibility analysis",
        )
        cls.FRICTION_SURFACE_ROLE = FilesetRole.objects.create(
            name="Friction surface",
            code=FilesetRoleCode.FRICTION_SURFACE,
            format=FilesetFormat.RASTER,
        )

        cls.TRAVEL_TIMES_ROLE = FilesetRole.objects.create(
            name="Friction surface",
            code=FilesetRoleCode.TRAVEL_TIMES,
            format=FilesetFormat.RASTER,
        )

    def test_webhook_not_authenticated_401(self):
        response = self.client.post(
            reverse(
                "connector_accessmod:webhook",
            ),
            {},
        )
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {"success": False},
        )

    def test_webhook_state_update_200(self):
        self.ACCESSIBILITY_ANALYSIS.status = AnalysisStatus.QUEUED
        self.ACCESSIBILITY_ANALYSIS.save()

        response = self.client.post(
            reverse(
                "connector_accessmod:webhook",
            ),
            {
                "id": str(uuid.uuid4()),
                "object": "event",
                "created": datetime.timestamp(timezone.now()),
                "type": "status_update",
                "data": {
                    "analysis_id": str(self.ACCESSIBILITY_ANALYSIS.id),
                    "status": AnalysisStatus.RUNNING,
                },
            },
            **{
                "HTTP_AUTHORIZATION": f"Bearer {b64encode(Signer().sign(self.DAG_RUN.webhook_token).encode('utf-8')).decode('utf-8')}"
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": True},
        )
        self.ACCESSIBILITY_ANALYSIS.refresh_from_db()
        self.assertEqual(AnalysisStatus.RUNNING, self.ACCESSIBILITY_ANALYSIS.status)

    def test_webhook_success_200(self):
        self.ACCESSIBILITY_ANALYSIS.status = AnalysisStatus.RUNNING
        self.ACCESSIBILITY_ANALYSIS.save()
        response = self.client.post(
            reverse(
                "connector_accessmod:webhook",
            ),
            {
                "id": str(uuid.uuid4()),
                "object": "event",
                "created": datetime.timestamp(timezone.now()),
                "type": "status_update",
                "data": {
                    "analysis_id": str(self.ACCESSIBILITY_ANALYSIS.id),
                    "status": AnalysisStatus.SUCCESS,
                    "outputs": {
                        "travel_times": "s3://some-bucket/some-dir/travel_times.tif",
                        "friction_surface": "s3://some-bucket/some-dir/friction_surface.tif",
                    },
                },
            },
            **{
                "HTTP_AUTHORIZATION": f"Bearer {b64encode(Signer().sign(self.DAG_RUN.webhook_token).encode('utf-8')).decode('utf-8')}"
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": True},
        )
        self.ACCESSIBILITY_ANALYSIS.refresh_from_db()
        self.assertEqual(AnalysisStatus.SUCCESS, self.ACCESSIBILITY_ANALYSIS.status)
        self.assertIsInstance(self.ACCESSIBILITY_ANALYSIS.travel_times, Fileset)
        self.assertEqual(1, self.ACCESSIBILITY_ANALYSIS.travel_times.file_set.count())
        self.assertIsInstance(self.ACCESSIBILITY_ANALYSIS.friction_surface, Fileset)
        self.assertEqual(
            1, self.ACCESSIBILITY_ANALYSIS.friction_surface.file_set.count()
        )
