from django.urls import reverse

from hexa.core.test import TestCase
from hexa.user_management.models import (
    Organization,
    OrganizationInvitation,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)


class OrganizationMembershipAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.STAFF = User.objects.create_user(
            "staff@openhexa.org", "password", is_staff=True, is_superuser=True
        )
        cls.JANE = User.objects.create_user("jane@openhexa.org", "password")
        cls.JOHN = User.objects.create_user("john@openhexa.org", "password")
        cls.ORG_A = Organization.objects.create(name="Alpha", short_name="alpha")
        cls.ORG_B = Organization.objects.create(name="Beta", short_name="beta")
        OrganizationMembership.objects.create(
            organization=cls.ORG_A,
            user=cls.JANE,
            role=OrganizationMembershipRole.OWNER,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORG_B,
            user=cls.JOHN,
            role=OrganizationMembershipRole.MEMBER,
        )
        OrganizationInvitation.objects.create(
            organization=cls.ORG_A,
            email="invited@openhexa.org",
            invited_by=cls.JANE,
            role=OrganizationMembershipRole.MEMBER,
        )

    def setUp(self):
        self.client.force_login(self.STAFF)

    def assertChangelistEmails(self, url_name, params, expected):
        response = self.client.get(reverse(url_name), params)
        self.assertEqual(response.status_code, 200)
        cl = response.context_data["cl"]
        emails = {getattr(obj, "user", obj).email for obj in cl.result_list}
        self.assertEqual(emails, expected)

    def test_memberships_can_be_filtered_and_searched(self):
        url_name = "admin:user_management_organizationmembership_changelist"
        self.assertChangelistEmails(
            url_name, {"role__exact": "owner"}, {"jane@openhexa.org"}
        )
        self.assertChangelistEmails(
            url_name,
            {"organization__id__exact": str(self.ORG_B.pk)},
            {"john@openhexa.org"},
        )
        self.assertChangelistEmails(url_name, {"q": "JANE@"}, {"jane@openhexa.org"})
        self.assertChangelistEmails(url_name, {"q": "beta"}, {"john@openhexa.org"})

    def test_invitations_can_be_filtered_and_searched(self):
        url_name = "admin:user_management_organizationinvitation_changelist"
        self.assertChangelistEmails(
            url_name, {"status__exact": "PENDING"}, {"invited@openhexa.org"}
        )
        self.assertChangelistEmails(url_name, {"status__exact": "ACCEPTED"}, set())
        self.assertChangelistEmails(url_name, {"q": "alpha"}, {"invited@openhexa.org"})

    def test_organization_picker_leaves_out_deleted_organizations(self):
        Organization.objects.create(
            name="Alpha Deleted", short_name="alpha-old"
        ).delete()
        response = self.client.get(
            reverse("admin:autocomplete"),
            {
                "term": "alpha",
                "app_label": "user_management",
                "model_name": "organizationmembership",
                "field_name": "organization",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [result["text"] for result in response.json()["results"]], ["alpha"]
        )
