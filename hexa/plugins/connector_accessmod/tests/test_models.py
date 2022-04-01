import responses
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ProtectedError

from hexa.core.test import TestCase
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    Analysis,
    AnalysisPermission,
    AnalysisStatus,
    File,
    Fileset,
    FilesetFormat,
    FilesetRole,
    FilesetRoleCode,
    Project,
    ProjectPermission,
)
from hexa.user_management.models import Membership, Team, User


class AccessmodModelsTest(TestCase):
    @classmethod
    @responses.activate
    def setUpTestData(cls):
        cls.USER_TAYLOR = User.objects.create_user(
            "taylor@bluesquarehub.com",
            "taylorrocks66",
        )
        cls.USER_SAM = User.objects.create_user(
            "sam@bluesquarehub.com",
            "samspasswOrD!!",
        )
        cls.USER_GRACE = User.objects.create_user(
            "grace@bluesquarehub.com",
            "grace_8798-:/",
        )
        cls.TEAM = Team.objects.create(name="Test Team")
        Membership.objects.create(user=cls.USER_SAM, team=cls.TEAM)
        Membership.objects.create(user=cls.USER_TAYLOR, team=cls.TEAM)
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

    def test_fileset_and_files_permissions_owner(self):
        fileset = Fileset.objects.create(
            name="A private slope",
            role=self.SLOPE_ROLE,
            project=self.SAMPLE_PROJECT,
            owner=self.USER_TAYLOR,
        )
        file = File.objects.create(
            fileset=fileset, uri="aprivatefile.tiff", mime_type="image/tiff"
        )
        self.assertEqual(
            fileset,
            Fileset.objects.filter_for_user(self.USER_TAYLOR).get(id=fileset.id),
        )
        self.assertEqual(
            file,
            File.objects.filter_for_user(self.USER_TAYLOR).get(id=file.id),
        )
        with self.assertRaises(ObjectDoesNotExist):
            Fileset.objects.filter_for_user(AnonymousUser()).get(id=fileset.id)
        with self.assertRaises(ObjectDoesNotExist):
            File.objects.filter_for_user(AnonymousUser()).get(id=file.id)
        with self.assertRaises(ObjectDoesNotExist):
            Fileset.objects.filter_for_user(self.USER_SAM).get(id=fileset.id)
        with self.assertRaises(ObjectDoesNotExist):
            File.objects.filter_for_user(self.USER_SAM).get(id=file.id)

    def test_fileset_and_files_permissions_team(self):
        ProjectPermission.objects.create(project=self.SAMPLE_PROJECT, team=self.TEAM)
        fileset = Fileset.objects.create(
            name="A private slope",
            role=self.SLOPE_ROLE,
            project=self.SAMPLE_PROJECT,
            owner=self.USER_TAYLOR,
        )
        file = File.objects.create(
            fileset=fileset, uri="aprivatefile.tiff", mime_type="image/tiff"
        )
        self.assertEqual(
            fileset,
            Fileset.objects.filter_for_user(self.USER_TAYLOR).get(id=fileset.id),
        )
        self.assertEqual(
            file,
            File.objects.filter_for_user(self.USER_TAYLOR).get(id=file.id),
        )
        self.assertEqual(
            fileset, Fileset.objects.filter_for_user(self.USER_SAM).get(id=fileset.id)
        )
        self.assertEqual(
            file, File.objects.filter_for_user(self.USER_SAM).get(id=file.id)
        )
        with self.assertRaises(ObjectDoesNotExist):
            Fileset.objects.filter_for_user(AnonymousUser()).get(id=fileset.id)
        with self.assertRaises(ObjectDoesNotExist):
            File.objects.filter_for_user(AnonymousUser()).get(id=file.id)
        with self.assertRaises(ObjectDoesNotExist):
            Fileset.objects.filter_for_user(self.USER_GRACE).get(id=fileset.id)
        with self.assertRaises(ObjectDoesNotExist):
            File.objects.filter_for_user(self.USER_GRACE).get(id=file.id)

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

    def test_analysis_permissions_owner(self):
        analysis = AccessibilityAnalysis.objects.create(
            owner=self.USER_TAYLOR,
            project=self.SAMPLE_PROJECT,
            name="Private accessibility analysis",
            slope=self.SLOPE_FILESET,
            priority_land_cover=[1, 2],
        )
        self.assertEqual(
            analysis,
            Analysis.objects.filter_for_user(self.USER_TAYLOR).get_subclass(
                id=analysis.id
            ),
        )
        with self.assertRaises(ObjectDoesNotExist):
            Analysis.objects.filter_for_user(AnonymousUser()).get_subclass(
                id=analysis.id
            )
        with self.assertRaises(ObjectDoesNotExist):
            Analysis.objects.filter_for_user(self.USER_SAM).get_subclass(id=analysis.id)

    def test_analysis_permissions_team(self):
        analysis = AccessibilityAnalysis.objects.create(
            owner=self.USER_TAYLOR,
            project=self.SAMPLE_PROJECT,
            name="Private accessibility analysis",
            slope=self.SLOPE_FILESET,
            priority_land_cover=[1, 2],
        )
        AnalysisPermission.objects.create(analysis=analysis, team=self.TEAM)
        self.assertEqual(
            analysis,
            Analysis.objects.filter_for_user(self.USER_TAYLOR).get_subclass(
                id=analysis.id
            ),
        )
        self.assertEqual(
            analysis,
            Analysis.objects.filter_for_user(self.USER_SAM).get_subclass(
                id=analysis.id
            ),
        )
        with self.assertRaises(ObjectDoesNotExist):
            Analysis.objects.filter_for_user(AnonymousUser()).get_subclass(
                id=analysis.id
            )
        with self.assertRaises(ObjectDoesNotExist):
            Analysis.objects.filter_for_user(self.USER_GRACE).get_subclass(
                id=analysis.id
            )
