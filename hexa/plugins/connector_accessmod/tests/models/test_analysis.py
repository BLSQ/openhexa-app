from unittest import skip

import responses
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist

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
    ProjectPermission,
)
from hexa.user_management.models import Membership, PermissionMode, Team, User


class AnalysisTest(TestCase):
    USER_TAYLOR = None
    USER_SAM = None
    USER_GRACE = None
    TEAM = None
    PROJECT_SAMPLE = None
    PROJECT_OTHER = None
    SLOPE_ROLE = None
    SLOPE_FILESET = None

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
        cls.PROJECT_SAMPLE = Project.objects.create(
            name="Sample project",
            country="BE",
            author=cls.USER_TAYLOR,
            spatial_resolution=100,
            crs=4326,
        )
        ProjectPermission.objects.create(
            user=cls.USER_TAYLOR, project=cls.PROJECT_SAMPLE, mode=PermissionMode.OWNER
        )
        cls.PROJECT_OTHER = Project.objects.create(
            name="Other project",
            country="BE",
            author=cls.USER_TAYLOR,
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
            project=cls.PROJECT_SAMPLE,
            author=cls.USER_TAYLOR,
        )
        cls.SLOPE_FILE = File.objects.create(
            fileset=cls.SLOPE_FILESET, uri="afile.tiff", mime_type="image/tiff"
        )
        cls.ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            author=cls.USER_TAYLOR,
            project=cls.PROJECT_SAMPLE,
            name="First accessibility analysis",
            slope=cls.SLOPE_FILESET,
            priority_land_cover=[1, 2],
        )
        cls.OTHER_ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            author=cls.USER_TAYLOR,
            project=cls.PROJECT_OTHER,
            name="Accessibility analysis with a common name",
            priority_land_cover=[1, 2],
        )
        cls.YET_ANOTHER_ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            author=cls.USER_TAYLOR,
            project=cls.PROJECT_SAMPLE,
            name="Yet another accessibility analysis",
        )

    def test_analysis_update_status_noop(self):
        analysis = AccessibilityAnalysis.objects.create(
            author=self.USER_TAYLOR,
            project=self.PROJECT_SAMPLE,
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

    def test_analysis_name_unique(self):
        self.assertEqual(
            1,
            AccessibilityAnalysis.objects.filter(
                name=self.OTHER_ACCESSIBILITY_ANALYSIS.name
            ).count(),
        )
        AccessibilityAnalysis.objects.create(
            author=self.USER_TAYLOR,
            project=self.PROJECT_SAMPLE,
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
        }
        self.ACCESSIBILITY_ANALYSIS.set_outputs(**outputs_1)

        outputs_2 = {
            "travel_times": "s3://some-bucket/some-dir/travel_times_2.tif",
            "friction_surface": "s3://some-bucket/some-dir/friction_surface_2.tif",
        }
        self.YET_ANOTHER_ACCESSIBILITY_ANALYSIS.set_outputs(**outputs_2)

    def test_analysis_permissions_owner(self):
        analysis = AccessibilityAnalysis.objects.create(
            author=self.USER_TAYLOR,
            project=self.PROJECT_SAMPLE,
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

    @skip
    def test_analysis_permissions_team(self):
        analysis = AccessibilityAnalysis.objects.create(
            author=self.USER_TAYLOR,
            project=self.PROJECT_SAMPLE,
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
