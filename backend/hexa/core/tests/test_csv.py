from django.http import HttpResponse

from hexa.core.test import TestCase
from hexa.user_management.models import Membership, Team, User

from ..csv import render_queryset_to_csv


class CsvTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_1 = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jim",
        )
        user_2 = User.objects.create_user(
            "mary@bluesquarehub.com",
            "mary",
        )
        team = Team.objects.create(name="Tèst Teâm")
        cls.MEMBERSHIP_1 = Membership.objects.create(team=team, user=user_1)
        cls.MEMBERSHIP_2 = Membership.objects.create(team=team, user=user_2)

    def test_render_queryset_to_csv(self):
        response = render_queryset_to_csv(
            Membership.objects.order_by("user__email"),
            filename="memberships.csv",
            field_names=[
                "id",
                "team.name",
                "user.email",
                "user.first_name",
                "user.foo.bar",
            ],
        )
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            "attachment;filename=memberships.csv",
            response.headers["content-Disposition"],
        )
        self.assertEqual(
            (
                "id,team_name,user_email,user_first_name,user_foo_bar\r\n"
                f"{self.MEMBERSHIP_1.id},Tèst Teâm,jim@bluesquarehub.com,,\r\n"
                f"{self.MEMBERSHIP_2.id},Tèst Teâm,mary@bluesquarehub.com,,\r\n"
            ).encode(),
            response.content,
        )
