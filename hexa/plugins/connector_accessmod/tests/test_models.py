import responses

from hexa.core.test import TestCase
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    AnalysisStatus,
    Project,
)
from hexa.user_management.models import User


class AccessmodModelsTest(TestCase):
    @classmethod
    @responses.activate
    def setUpTestData(cls):
        cls.USER_TAYLOR = User.objects.create_user(
            "taylor@bluesquarehub.com",
            "taylorrocks66",
            is_superuser=True,
        )
        cls.SAMPLE_PROJECT = Project.objects.create(
            name="Sample project",
            country="BE",
            owner=cls.USER_TAYLOR,
            spatial_resolution=100,
            crs=4326,
        )

    def test_analysis_update_status_noop(self):
        analysis = AccessibilityAnalysis.objects.create(
            owner=self.USER_TAYLOR,
            project=self.SAMPLE_PROJECT,
            name="Test accessibility analysis",
            status=AnalysisStatus.RUNNING,
        )
        analysis.update_status(AnalysisStatus.RUNNING)
        self.assertEqual(analysis.status, AnalysisStatus.RUNNING)

        analysis.status = AnalysisStatus.SUCCESS
        analysis.save()
        analysis.update_status(AnalysisStatus.RUNNING)
        self.assertEqual(analysis.status, AnalysisStatus.SUCCESS)

        analysis.status = AnalysisStatus.FAILED
        analysis.save()
        analysis.update_status(AnalysisStatus.RUNNING)
        self.assertEqual(analysis.status, AnalysisStatus.FAILED)
