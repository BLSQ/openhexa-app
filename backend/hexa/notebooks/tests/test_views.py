from django.urls import reverse

from hexa.core.test import TestCase
from hexa.user_management.models import User


class ViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
            is_superuser=True,
        )

    def test_credentials_200(self):
        self.client.force_login(self.USER_JANE)
        response = self.client.post(
            reverse(
                "notebooks:credentials",
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "username": "jane@bluesquarehub.com",
                "env": {"GIT_EXTENSION_ENABLED": "false"},
                "files": {},
            },
        )

    def test_credentials_401(self):
        response = self.client.post(reverse("notebooks:credentials"))

        self.assertEqual(response.status_code, 401)
        response_data = response.json()
        self.assertEqual(0, len(response_data))

    def test_authenticate_200(self):
        self.client.force_login(self.USER_JANE)
        response = self.client.post(
            reverse(
                "notebooks:authenticate",
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "username": "jane@bluesquarehub.com",
            },
        )

    def test_authenticate_302(self):
        response = self.client.post(
            reverse(
                "notebooks:authenticate",
            ),
        )
        self.assertRedirects(
            response,
            "/login?next={}".format(
                reverse(
                    "notebooks:authenticate",
                )
            ),
            fetch_redirect_response=False,
        )

    def test_default_credentials_200(self):
        self.client.force_login(self.USER_JANE)
        response = self.client.post(
            reverse(
                "notebooks:default-credentials",
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "username": "jane@bluesquarehub.com",
                "env": {"GIT_EXTENSION_ENABLED": "false"},
                "files": {},
            },
        )

    def test_default_credentials_302(self):
        response = self.client.post(
            reverse(
                "notebooks:default-credentials",
            ),
        )
        self.assertRedirects(
            response,
            "/login?next={}".format(
                reverse(
                    "notebooks:default-credentials",
                )
            ),
            fetch_redirect_response=False,
        )
