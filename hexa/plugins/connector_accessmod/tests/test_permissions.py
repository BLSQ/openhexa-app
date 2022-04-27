import responses

from hexa.core.test import TestCase
from hexa.plugins.connector_accessmod.models import (
    Fileset,
    FilesetFormat,
    FilesetRole,
    FilesetRoleCode,
    Project,
    ProjectPermission,
)
from hexa.user_management.models import (
    Membership,
    MembershipRole,
    PermissionMode,
    Team,
    User,
)


class PermissionsTest(TestCase):
    USER_MIRANDA = None
    USER_JENNY = None
    USER_GERALD = None
    TEAM = None
    PROJECT_1 = None
    PROJECT_2 = None
    SLOPE_ROLE = None

    @classmethod
    @responses.activate
    def setUpTestData(cls):
        cls.USER_MIRANDA = User.objects.create_user(
            "miranda@bluesquarehub.com",
            "mirandasthebest",
        )
        cls.USER_JENNY = User.objects.create_user(
            "jenny@bluesquarehub.com",
            "yoimjenny!",
        )
        cls.USER_GERALD = User.objects.create_user(
            "gerald@bluesquarehub.com",
            "gerald2000",
        )
        cls.TEAM = Team.objects.create(name="Test Team")
        Membership.objects.create(
            user=cls.USER_MIRANDA, team=cls.TEAM, role=MembershipRole.ADMIN
        )
        Membership.objects.create(
            user=cls.USER_JENNY, team=cls.TEAM, role=MembershipRole.REGULAR
        )
        cls.PROJECT_1 = Project.objects.create(
            name="First project",
            country="BE",
            author=cls.USER_MIRANDA,
            spatial_resolution=100,
            crs=4326,
        )
        cls.PROJECT_2 = Project.objects.create(
            name="Second project",
            country="BE",
            author=cls.USER_MIRANDA,
            spatial_resolution=100,
            crs=4326,
        )
        ProjectPermission.objects.create(
            user=cls.USER_MIRANDA, project=cls.PROJECT_1, mode=PermissionMode.OWNER
        )
        ProjectPermission.objects.create(
            team=cls.TEAM, project=cls.PROJECT_2, mode=PermissionMode.OWNER
        )
        cls.SLOPE_ROLE = FilesetRole.objects.create(
            name="Slope",
            code=FilesetRoleCode.SLOPE,
            format=FilesetFormat.RASTER,
        )

    def test_create_file_permission_individual(self):
        fileset = Fileset.objects.create(
            name="A beautiful slope",
            role=self.SLOPE_ROLE,
            project=self.PROJECT_1,
            author=self.USER_MIRANDA,
        )
        self.assertTrue(
            self.USER_MIRANDA.has_perm("connector_accessmod.create_file", fileset)
        )
        self.assertFalse(
            self.USER_JENNY.has_perm("connector_accessmod.create_file", fileset)
        )
        self.assertFalse(
            self.USER_GERALD.has_perm("connector_accessmod.create_file", fileset)
        )

    def test_create_file_permission_team(self):
        fileset = Fileset.objects.create(
            name="An amazing slope",
            role=self.SLOPE_ROLE,
            project=self.PROJECT_2,
            author=self.USER_MIRANDA,
        )
        self.assertTrue(
            self.USER_MIRANDA.has_perm("connector_accessmod.create_file", fileset)
        )
        self.assertTrue(
            self.USER_JENNY.has_perm("connector_accessmod.create_file", fileset)
        )
        self.assertFalse(
            self.USER_GERALD.has_perm("connector_accessmod.create_file", fileset)
        )
