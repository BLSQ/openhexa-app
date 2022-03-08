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
        cls.OTHER_PROJECT = Project.objects.create(
            name="Other project",
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
        cls.CATCHMENT_AREAS_ROLE = FilesetRole.objects.create(
            name="Catchment areas",
            code=FilesetRoleCode.CATCHMENT_AREAS,
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
        cls.OTHER_ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            owner=cls.USER_TAYLOR,
            project=cls.OTHER_PROJECT,
            name="Accessibility analysis with a common name",
            priority_land_cover=[1, 2],
        )
        cls.YET_ANOTHER_ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            owner=cls.USER_TAYLOR,
            project=cls.SAMPLE_PROJECT,
            name="Yet another accessibility analysis",
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
        """Cascade delete Project > Fileset > File & Project > Analysis"""

        self.assertEqual(2, Project.objects.filter().count())
        self.assertEqual(3, Analysis.objects.filter().count())
        self.SAMPLE_PROJECT.delete()
        self.assertEqual(1, Project.objects.filter().count())
        self.assertEqual(1, Analysis.objects.count())
        self.assertEqual(0, Fileset.objects.count())
        self.assertEqual(0, File.objects.count())

    def test_fileset_delete(self):
        """Cascade delete Fileset > File"""
        with self.assertRaises(
            ProtectedError
        ):  # Can't delete filesets if used in an analysis
            self.SLOPE_FILESET.delete()

        self.ACCESSIBILITY_ANALYSIS.slope = None
        self.ACCESSIBILITY_ANALYSIS.save()
        self.SLOPE_FILESET.delete()
        self.assertEqual(0, File.objects.count())

    def test_analysis_name_unique(self):
        self.assertEqual(
            1,
            AccessibilityAnalysis.objects.filter(
                name=self.OTHER_ACCESSIBILITY_ANALYSIS.name
            ).count(),
        )
        AccessibilityAnalysis.objects.create(
            owner=self.USER_TAYLOR,
            project=self.SAMPLE_PROJECT,
            name=self.OTHER_ACCESSIBILITY_ANALYSIS.name,
        )
        self.assertEqual(
            2,
            AccessibilityAnalysis.objects.filter(
                name=self.OTHER_ACCESSIBILITY_ANALYSIS.name
            ).count(),
        )

    def test_analysis_set_outputs(self):
        """Test outputs handling, including possible name conflicts"""

        outputs_1 = {
            "travel_times": "s3://some-bucket/some-dir/travel_times_1.tif",
            "friction_surface": "s3://some-bucket/some-dir/friction_surface_1.tif",
            "catchment_areas": "s3://some-bucket/some-dir/catchment_areas_1.tif",
        }
        self.ACCESSIBILITY_ANALYSIS.set_outputs(**outputs_1)

        outputs_2 = {
            "travel_times": "s3://some-bucket/some-dir/travel_times_2.tif",
            "friction_surface": "s3://some-bucket/some-dir/friction_surface_2.tif",
            "catchment_areas": "s3://some-bucket/some-dir/catchment_areas_2.tif",
        }
        self.YET_ANOTHER_ACCESSIBILITY_ANALYSIS.set_outputs(**outputs_2)
