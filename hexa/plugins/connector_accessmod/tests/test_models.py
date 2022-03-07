import responses

from hexa.core.test import TestCase
from hexa.plugins.connector_accessmod.models import AccessibilityAnalysis, Project
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
        cls.ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            owner=cls.USER_TAYLOR,
            project=cls.SAMPLE_PROJECT,
            name="Test accessibility analysis",
        )

    def test_analysis_update_status_noop(self):
        self.ACCESSIBILITY_ANALYSIS.update_status(self.ACCESSIBILITY_ANALYSIS.status)
