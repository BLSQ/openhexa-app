import base64
import json

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
    FilesetStatus,
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
    WATER_ROLE = None
    WATER_FILESET = None

    @classmethod
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
            team=cls.TEAM, project=cls.PROJECT_SAMPLE, mode=PermissionMode.OWNER
        )
        cls.PROJECT_OTHER = Project.objects.create(
            name="Other project",
            country="BE",
            author=cls.USER_TAYLOR,
            spatial_resolution=100,
            crs=4326,
        )
        cls.WATER_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.WATER,
        )
        cls.FRICTION_SURFACE_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.FRICTION_SURFACE,
        )
        cls.TRAVEL_TIMES_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.TRAVEL_TIMES,
        )
        cls.WATER_FILESET = Fileset.objects.create(
            name="A beautiful water fileset",
            role=cls.WATER_ROLE,
            project=cls.PROJECT_SAMPLE,
            author=cls.USER_TAYLOR,
        )
        cls.WATER_FILE = File.objects.create(
            fileset=cls.WATER_FILESET, uri="afile.tiff", mime_type="image/tiff"
        )
        cls.ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            author=cls.USER_TAYLOR,
            project=cls.PROJECT_SAMPLE,
            name="First accessibility analysis",
            water=cls.WATER_FILESET,
        )
        cls.OTHER_ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            author=cls.USER_TAYLOR,
            project=cls.PROJECT_OTHER,
            name="Accessibility analysis with a common name",
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
            water=self.WATER_FILESET,
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
            Analysis.objects.filter_for_user(self.USER_GRACE).get_subclass(
                id=analysis.id
            )

    def test_analysis_permissions_team(self):
        analysis = AccessibilityAnalysis.objects.create(
            author=self.USER_TAYLOR,
            project=self.PROJECT_SAMPLE,
            name="Private accessibility analysis",
            water=self.WATER_FILESET,
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


class AnalysisBuildConfTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.PROJECT = Project.objects.create(
            name="Jimmy's project",
            country="BE",
            author=None,
            spatial_resolution=100,
            crs=6933,
        )
        cls.PROJECT_2 = Project.objects.create(
            name="A project",
            country="FR",
            author=None,
            spatial_resolution=100,
            crs=6933,
        )

        def make_file(project, role, status):
            fsr = FilesetRole.objects.create(
                name=role,
                code=getattr(FilesetRoleCode, role),
                format=FilesetFormat.RASTER,
            )
            fs = Fileset.objects.create(
                project=project,
                name=f"{fsr.id}_{role}",
                status=getattr(FilesetStatus, status),
                role=fsr,
                author=None,
            )
            file = File.objects.create(
                mime_type="image/geotiff",
                uri=f"s3://some-bucket/{fs.id}/some-file",
                fileset=fs,
            )
            setattr(cls, role + "_ROLE", fsr)
            setattr(cls, role + "_FS", fs)
            setattr(cls, role + "_FILE", file)
            return fs

        cls.ANALYSIS_NOACQ = AccessibilityAnalysis.objects.create(
            author=None,
            project=cls.PROJECT,
            name="analysis no acquisition",
            water=make_file(cls.PROJECT, "WATER", "PENDING"),
            transport_network=make_file(cls.PROJECT, "TRANSPORT_NETWORK", "PENDING"),
            land_cover=make_file(cls.PROJECT, "LAND_COVER", "PENDING"),
            dem=make_file(cls.PROJECT, "DEM", "PENDING"),
            health_facilities=make_file(cls.PROJECT, "HEALTH_FACILITIES", "PENDING"),
        )

        cls.ANALYSIS_FULLACQ = AccessibilityAnalysis.objects.create(
            author=None,
            project=cls.PROJECT,
            name="analysis full acquisition",
            water=make_file(cls.PROJECT, "WATER", "TO_ACQUIRE"),
            transport_network=make_file(cls.PROJECT, "TRANSPORT_NETWORK", "TO_ACQUIRE"),
            land_cover=make_file(cls.PROJECT, "LAND_COVER", "TO_ACQUIRE"),
            dem=make_file(cls.PROJECT, "DEM", "TO_ACQUIRE"),
            health_facilities=make_file(cls.PROJECT, "HEALTH_FACILITIES", "TO_ACQUIRE"),
        )
        cls.ANALYSIS_MINIMAL = AccessibilityAnalysis.objects.create(
            author=None,
            project=cls.PROJECT,
            name="minimal analysis wihtout stack",
            water=None,
            transport_network=None,
            land_cover=None,
            dem=make_file(cls.PROJECT, "DEM", "TO_ACQUIRE"),
            health_facilities=make_file(cls.PROJECT, "HEALTH_FACILITIES", "TO_ACQUIRE"),
        )

    def test_build_dag_noacq(self):
        config = self.ANALYSIS_NOACQ.build_dag_conf("s3://S/")
        for acquisition in (
            "acquisition_healthsites",
            "acquisition_copernicus",
            "acquisition_osm",
            "acquisition_srtm",
        ):
            self.assertEqual(config[acquisition], False)

        am_config = json.loads(base64.b64decode(config["am_config"]))
        self.assertEqual(am_config["crs"], 6933)
        self.assertEqual(am_config["country"]["name"], "Belgium")
        self.assertEqual(am_config["spatial_resolution"], 100)
        self.assertEqual(am_config["dem"]["auto"], False)

    def test_build_dag_fullacq(self):
        config = self.ANALYSIS_FULLACQ.build_dag_conf("s3://S/")
        for acquisition in (
            "acquisition_healthsites",
            "acquisition_copernicus",
            "acquisition_osm",
            "acquisition_srtm",
        ):
            self.assertEqual(config[acquisition], True)

        am_config = json.loads(base64.b64decode(config["am_config"]))
        self.assertEqual(am_config["crs"], 6933)
        self.assertEqual(am_config["country"]["name"], "Belgium")
        self.assertEqual(am_config["spatial_resolution"], 100)
        self.assertEqual(am_config["dem"]["auto"], True)

    def test_build_dag_user_stack(self):
        fsr = FilesetRole.objects.create(
            name="STACK",
            code=FilesetRoleCode.STACK,
            format=FilesetFormat.RASTER,
        )
        fs = Fileset.objects.create(
            project=self.PROJECT,
            name=f"{fsr.id}_STACK",
            status=FilesetStatus.VALID,
            role=fsr,
            author=None,
        )
        File.objects.create(
            mime_type="image/geotiff",
            uri=f"s3://some-bucket/{fs.id}/some-file",
            fileset=fs,
        )
        self.ANALYSIS_MINIMAL.stack = fs
        self.ANALYSIS_MINIMAL.save()

        self.assertEqual(self.ANALYSIS_MINIMAL.status, AnalysisStatus.READY)
        config = self.ANALYSIS_MINIMAL.build_dag_conf("s3://S/")
        am_config = json.loads(base64.b64decode(config["am_config"]))

        self.assertTrue("priorities" not in am_config)
        self.assertEqual(am_config["stack"]["name"], self.ANALYSIS_MINIMAL.stack.name)
