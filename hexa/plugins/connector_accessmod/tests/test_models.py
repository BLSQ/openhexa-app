import responses
from django.db.models import ProtectedError

from hexa.core.test import TestCase
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    Analysis,
    AnalysisStatus,
    File,
    Fileset,
    FilesetFormat,
    FilesetRole,
    FilesetRoleCode,
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
        cls.SLOPE_ROLE = FilesetRole.objects.create(
            name="Slope",
            code=FilesetRoleCode.SLOPE,
            format=FilesetFormat.RASTER,
        )
        cls.SLOPE_FILESET = Fileset.objects.create(
            name="A beautiful slope",
            role=cls.SLOPE_ROLE,
            project=cls.SAMPLE_PROJECT,
            owner=cls.USER_TAYLOR,
        )
        cls.SLOPE_FILE = File.objects.create(
            fileset=cls.SLOPE_FILESET, uri="afile.tiff", mime_type="image/tiff"
        )
        cls.ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            owner=cls.USER_TAYLOR,
            project=cls.SAMPLE_PROJECT,
            name="First accessibility analysis",
            slope=cls.SLOPE_FILESET,
            priority_land_cover=[1, 2],
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

    def test_project_delete(self):
        # Cascade delete Project > Fileset > File & Project > Analysis
        self.SAMPLE_PROJECT.delete()
        self.assertEqual(0, Project.objects.count())
        self.assertEqual(0, Fileset.objects.count())
        self.assertEqual(0, File.objects.count())
        self.assertEqual(0, Analysis.objects.count())

    def test_fileset_delete(self):
        # Can't delete filesets if used in an analysis
        with self.assertRaises(ProtectedError):
            self.SLOPE_FILESET.delete()

        # Cascade delete Fileset > File
        self.ACCESSIBILITY_ANALYSIS.slope = None
        self.ACCESSIBILITY_ANALYSIS.save()
        self.SLOPE_FILESET.delete()
        self.assertEqual(0, File.objects.count())
