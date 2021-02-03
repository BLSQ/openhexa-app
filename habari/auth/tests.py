from django.conf import settings
from django import test


class SimpleTest(test.TestCase):
    def test_index_redirects_to_login(self):
        response = self.client.get("/")

        # Check that the response is temporary redirection to /login.
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login", response.url)

    def test_login_200(self):
        response = self.client.get(settings.LOGIN_URL)

        self.assertEqual(response.status_code, 200)
