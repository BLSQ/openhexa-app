import responses
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist

from hexa.core.test import TestCase
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    Analysis,
    File,
    Fileset,
    Project,
    ProjectPermission,
)
from hexa.user_management.models import Membership, Team, User


class AccessmodModelsTest(TestCase):
    USER_HUNTER = None
    USER_JIMMY = None
    USER_HANNAH = None
    TEAM = None
    PROJECT_SAMPLE = None
    PROJECT_OTHER = None

    @classmethod
    @responses.activate
    def setUpTestData(cls):
        cls.USER_HUNTER = User.objects.create_user(
            "hunter@bluesquarehub.com",
            "hunterrocks66",
        )
        cls.USER_JIMMY = User.objects.create_user(
            "jimmy@bluesquarehub.com",
            "jimmyspasswOrD!!",
        )
        cls.USER_HANNAH = User.objects.create_user(
            "hannah@bluesquarehub.com",
            "hannah_8798-:/",
        )
        cls.TEAM = Team.objects.create(name="Test Team")
        Membership.objects.create(user=cls.USER_JIMMY, team=cls.TEAM)
        Membership.objects.create(user=cls.USER_HUNTER, team=cls.TEAM)

        cls.PROJECT_SAMPLE = Project.objects.create(
            name="jimmyple project",
            country="BE",
            owner=cls.USER_HUNTER,
            spatial_resolution=100,
            crs=4326,
        )
        cls.PROJECT_OTHER = Project.objects.create(
            name="Other project",
            country="BE",
            owner=cls.USER_HUNTER,
            spatial_resolution=100,
            crs=4326,
        )

        cls.ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            owner=cls.USER_HUNTER,
            project=cls.PROJECT_SAMPLE,
            name="First accessibility analysis",
            priority_land_cover=[1, 2],
        )
        cls.OTHER_ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            owner=cls.USER_HANNAH,
            project=cls.PROJECT_OTHER,
            name="Accessibility analysis with a common name",
            priority_land_cover=[1, 2],
        )
        cls.YET_ANOTHER_ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            owner=cls.USER_HANNAH,
            project=cls.PROJECT_SAMPLE,
            name="Yet another accessibility analysis",
        )

    def test_project_permissions_owner(self):
        project = Project.objects.create(
            name="Private project",
            country="BE",
            owner=self.USER_HUNTER,
            spatial_resolution=100,
            crs=4326,
        )
        self.assertEqual(
            project,
            Project.objects.filter_for_user(self.USER_HUNTER).get(id=project.id),
        )
        with self.assertRaises(ObjectDoesNotExist):
            Project.objects.filter_for_user(AnonymousUser()).get(id=project.id)
        with self.assertRaises(ObjectDoesNotExist):
            Project.objects.filter_for_user(self.USER_JIMMY).get(id=project.id)

    def test_project_permissions_team(self):
        project = Project.objects.create(
            name="Private project",
            country="BE",
            owner=self.USER_HUNTER,
            spatial_resolution=100,
            crs=4326,
        )
        ProjectPermission.objects.create(project=project, team=self.TEAM)
        self.assertEqual(
            project,
            Project.objects.filter_for_user(self.USER_HUNTER).get(id=project.id),
        )
        self.assertEqual(
            project, Project.objects.filter_for_user(self.USER_JIMMY).get(id=project.id)
        )
        with self.assertRaises(ObjectDoesNotExist):
            Project.objects.filter_for_user(AnonymousUser()).get(id=project.id)
        with self.assertRaises(ObjectDoesNotExist):
            Project.objects.filter_for_user(self.USER_HANNAH).get(id=project.id)

    def test_project_delete(self):
        """Cascade delete Project > Fileset > File & Project > Analysis"""

        self.assertEqual(2, Project.objects.filter().count())
        self.assertEqual(3, Analysis.objects.filter().count())
        self.PROJECT_SAMPLE.delete()
        self.assertEqual(1, Project.objects.filter().count())
        self.assertEqual(1, Analysis.objects.count())
        self.assertEqual(0, Fileset.objects.count())
        self.assertEqual(0, File.objects.count())
