from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ProtectedError

from hexa.core.test import TestCase
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    File,
    Fileset,
    FilesetMode,
    FilesetRole,
    FilesetRoleCode,
    FilesetStatus,
    Project,
    ProjectPermission,
)
from hexa.user_management.models import Membership, PermissionMode, Team, User


class FilesetTest(TestCase):
    USER_SIMONE = None
    USER_ROBERT = None
    USER_DONALD = None
    TEAM = None
    PROJECT_SAMPLE = None
    WATER_ROLE = None
    WATER_FILESET = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_SIMONE = User.objects.create_user(
            "simone@bluesquarehub.com",
            "simonerocks66",
        )
        cls.USER_ROBERT = User.objects.create_user(
            "robert@bluesquarehub.com",
            "robert2000",
        )
        cls.USER_DONALD = User.objects.create_user(
            "donald@bluesquarehub.com",
            "donald^^",
        )
        cls.TEAM = Team.objects.create(name="Some Team")
        Membership.objects.create(user=cls.USER_ROBERT, team=cls.TEAM)
        Membership.objects.create(user=cls.USER_SIMONE, team=cls.TEAM)
        cls.PROJECT_SAMPLE = Project.objects.create(
            name="Sample project",
            country="BE",
            author=cls.USER_SIMONE,
            spatial_resolution=100,
            crs=4326,
        )
        ProjectPermission.objects.create(
            user=cls.USER_SIMONE, project=cls.PROJECT_SAMPLE, mode=PermissionMode.OWNER
        )
        cls.PROJECT_OTHER = Project.objects.create(
            name="Another project",
            country="BE",
            author=cls.USER_SIMONE,
            spatial_resolution=100,
            crs=4326,
        )
        cls.WATER_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.WATER,
        )
        cls.WATER_FILESET = Fileset.objects.create(
            name="A beautiful water",
            role=cls.WATER_ROLE,
            project=cls.PROJECT_SAMPLE,
            author=cls.USER_SIMONE,
        )
        cls.WATER_FILE = File.objects.create(
            fileset=cls.WATER_FILESET, uri="afile.tiff", mime_type="image/tiff"
        )
        cls.ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            author=cls.USER_SIMONE,
            project=cls.PROJECT_SAMPLE,
            name="First accessibility analysis",
            water=cls.WATER_FILESET,
        )

    def test_fileset_and_files_permissions_owner(self):
        fileset = Fileset.objects.create(
            name="A private water",
            role=self.WATER_ROLE,
            project=self.PROJECT_SAMPLE,
            author=self.USER_SIMONE,
        )
        file = File.objects.create(
            fileset=fileset, uri="aprivatefile.tiff", mime_type="image/tiff"
        )
        self.assertEqual(
            fileset,
            Fileset.objects.filter_for_user(self.USER_SIMONE).get(id=fileset.id),
        )
        self.assertEqual(
            file,
            File.objects.filter_for_user(self.USER_SIMONE).get(id=file.id),
        )
        with self.assertRaises(ObjectDoesNotExist):
            Fileset.objects.filter_for_user(AnonymousUser()).get(id=fileset.id)
        with self.assertRaises(ObjectDoesNotExist):
            File.objects.filter_for_user(AnonymousUser()).get(id=file.id)
        with self.assertRaises(ObjectDoesNotExist):
            Fileset.objects.filter_for_user(self.USER_ROBERT).get(id=fileset.id)
        with self.assertRaises(ObjectDoesNotExist):
            File.objects.filter_for_user(self.USER_ROBERT).get(id=file.id)

    def test_fileset_and_files_permissions_team(self):
        ProjectPermission.objects.create(project=self.PROJECT_SAMPLE, team=self.TEAM)
        fileset = Fileset.objects.create(
            name="A private water",
            role=self.WATER_ROLE,
            project=self.PROJECT_SAMPLE,
            author=self.USER_SIMONE,
        )
        file = File.objects.create(
            fileset=fileset, uri="aprivatefile.tiff", mime_type="image/tiff"
        )
        self.assertEqual(
            fileset,
            Fileset.objects.filter_for_user(self.USER_SIMONE).get(id=fileset.id),
        )
        self.assertEqual(
            file,
            File.objects.filter_for_user(self.USER_SIMONE).get(id=file.id),
        )
        self.assertEqual(
            fileset,
            Fileset.objects.filter_for_user(self.USER_ROBERT).get(id=fileset.id),
        )
        self.assertEqual(
            file, File.objects.filter_for_user(self.USER_ROBERT).get(id=file.id)
        )
        with self.assertRaises(ObjectDoesNotExist):
            Fileset.objects.filter_for_user(AnonymousUser()).get(id=fileset.id)
        with self.assertRaises(ObjectDoesNotExist):
            File.objects.filter_for_user(AnonymousUser()).get(id=file.id)
        with self.assertRaises(ObjectDoesNotExist):
            Fileset.objects.filter_for_user(self.USER_DONALD).get(id=fileset.id)
        with self.assertRaises(ObjectDoesNotExist):
            File.objects.filter_for_user(self.USER_DONALD).get(id=file.id)

    def test_fileset_delete(self):
        """Cascade delete Fileset > File"""
        with self.assertRaises(
            ProtectedError
        ):  # Can't delete filesets if used in an analysis
            self.WATER_FILESET.delete()

        self.ACCESSIBILITY_ANALYSIS.water = None
        self.ACCESSIBILITY_ANALYSIS.save()
        self.WATER_FILESET.delete()
        self.assertEqual(0, File.objects.count())

    def test_fileset_create_if_has_perm(self):
        fileset = Fileset.objects.create_if_has_perm(
            principal=self.USER_SIMONE,
            name="Look it's a sea",
            role=self.WATER_ROLE,
            project=self.PROJECT_SAMPLE,
        )
        self.assertEqual(FilesetStatus.PENDING, fileset.status)
        self.assertEqual(FilesetMode.USER_INPUT, fileset.mode)

        fileset = Fileset.objects.create_if_has_perm(
            principal=self.USER_SIMONE,
            name="What a beautiful lake",
            role=self.WATER_ROLE,
            project=self.PROJECT_SAMPLE,
            automatic_acquisition=False,
        )
        self.assertEqual(FilesetStatus.PENDING, fileset.status)
        self.assertEqual(FilesetMode.USER_INPUT, fileset.mode)

        fileset = Fileset.objects.create_if_has_perm(
            principal=self.USER_SIMONE,
            name="Just a small pond...",
            role=self.WATER_ROLE,
            project=self.PROJECT_SAMPLE,
            automatic_acquisition=True,
        )
        self.assertEqual(FilesetStatus.TO_ACQUIRE, fileset.status)
        self.assertEqual(FilesetMode.AUTOMATIC_ACQUISITION, fileset.mode)
