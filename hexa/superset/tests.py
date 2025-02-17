import requests_mock

from hexa.core.test import TestCase
from hexa.superset.api import SupersetAuthError
from hexa.superset.models import SupersetInstance


class SupersetTestCase(TestCase):
    def setUp(self):
        self.superset_instance = SupersetInstance.objects.create(
            name="Superset",
            url="https://superset.com",
            api_username="test",
            api_password="password",
        )

    def test_superset_dashboard(self):
        self.assertEqual(self.superset_instance.name, "Superset")
        self.assertEqual(self.superset_instance.url, "https://superset.com")
        self.assertEqual(self.superset_instance.api_username, "test")
        self.assertEqual(self.superset_instance.api_password, "password")

    def test_get_client(self):
        client = self.superset_instance.get_client()
        self.assertEqual(client.url, "https://superset.com")
        self.assertEqual(client.username, "test")
        self.assertEqual(client.password, "password")

    def test_client_authenticate_success(self):
        client = self.superset_instance.get_client()

        # We need to intercept the requests that the client makes
        # and check that the client is authenticated
        with requests_mock.Mocker() as mocker:
            mocker.post(
                "https://superset.com/api/v1/security/login",
                status_code=200,
                json={"access_token": "access_token"},
            )
            mocker.get(
                "https://superset.com/api/v1/security/csrf_token/",
                status_code=200,
                headers={"Set-Cookie": "cookie"},
                json={"result": "csrf_token"},
            )
            client.authenticate()
        self.assertEqual(client.session.headers["Authorization"], "Bearer access_token")
        self.assertEqual(client.session.headers["X-CSRF-TOKEN"], "csrf_token")
        self.assertEqual(client.session.headers["Cookie"], "cookie")
        self.assertEqual(client.session.headers["Referer"], "https://superset.com")

    def test_client_authenticate_failure(self):
        client = self.superset_instance.get_client()
        with requests_mock.Mocker() as mocker:
            mocker.post(
                "https://superset.com/api/v1/security/login",
                status_code=401,
            )
            with self.assertRaises(SupersetAuthError):
                client.authenticate()

    def test_get_guest_token(self):
        client = self.superset_instance.get_client()
        with requests_mock.Mocker() as mocker:
            mocker.post(
                "https://superset.com/api/v1/security/login",
                status_code=200,
                json={"access_token": "access_token"},
            )
            mocker.get(
                "https://superset.com/api/v1/security/csrf_token/",
                status_code=200,
                headers={"Set-Cookie": "cookie"},
                json={"result": "csrf_token"},
            )
            mocker.post(
                "https://superset.com/api/v1/security/guest_token/",
                status_code=200,
                json={"token": "guest_token"},
            )
            guest_token = client.get_guest_token(
                user={"username": "test", "first_name": "Test", "last_name": "User"},
                resources=[{"type": "dashboard", "id": "1"}],
            )
            self.assertEqual(guest_token, "guest_token")
            self.assertEqual(
                mocker.last_request.json(),
                {
                    "user": {
                        "username": "test",
                        "first_name": "Test",
                        "last_name": "User",
                    },
                    "resources": [{"type": "dashboard", "id": "1"}],
                    "rls": [],
                },
            )
