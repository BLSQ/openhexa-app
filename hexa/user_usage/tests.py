from django import test
from django.urls import reverse

from hexa.user_management.models import User
from hexa.user_usage.models import WebHit


class WebHitsTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_FOO = User.objects.create_user(
            "foo@bluesquarehub.com",
            "Foo Bar",
        )

    @test.override_settings(SAVE_WEB_HITS=True)
    def test_save_webhits_200(self):
        self.client.force_login(self.USER_FOO)
        whc1 = WebHit.objects.count()
        response = self.client.get(
            reverse(
                "catalog:index",
            ),
        )
        whc2 = WebHit.objects.count()
        self.assertEqual(whc1 + 1, whc2)
