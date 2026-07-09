import hashlib
from datetime import timedelta

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone

from hexa.user_management.models import User
from hexa.webapps.middlewares import (
    PREVIEW_KEYS_FIELD,
    get_or_create_preview_session_key,
)
from hexa.webapps.models import Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)

WEBAPPS_DOMAIN = "webapps.test.local"


class PreviewSessionKeyTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("preview@test.com", "password")
        cls.WORKSPACE = Workspace.objects.create(name="Preview WS")
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.WEBAPP = Webapp.objects.create(
            name="App One",
            slug="app-one",
            subdomain="app-one",
            url="http://example.com",
            workspace=cls.WORKSPACE,
            created_by=cls.USER,
        )
        cls.WEBAPP_2 = Webapp.objects.create(
            name="App Two",
            slug="app-two",
            subdomain="app-two",
            url="http://example.com",
            workspace=cls.WORKSPACE,
            created_by=cls.USER,
        )

    def _request_with_session(self):
        request = RequestFactory().get("/")
        request.session = SessionStore()
        request.session.create()
        return request

    def test_key_is_random_reused_and_not_legacy_hash(self):
        request = self._request_with_session()
        first = get_or_create_preview_session_key(request, self.WEBAPP, self.USER)
        second = get_or_create_preview_session_key(request, self.WEBAPP, self.USER)

        self.assertRegex(first, r"^[a-z0-9]{32}$")
        self.assertEqual(first, second)  # reused within one main session

        legacy = hashlib.sha256(
            f"{self.USER.pk}:{self.WEBAPP.pk}:{settings.SECRET_KEY}".encode()
        ).hexdigest()[:32]
        self.assertNotEqual(first, legacy)

    def test_distinct_webapps_get_distinct_keys(self):
        request = self._request_with_session()
        first = get_or_create_preview_session_key(request, self.WEBAPP, self.USER)
        other = get_or_create_preview_session_key(request, self.WEBAPP_2, self.USER)
        self.assertNotEqual(first, other)

    def test_expired_pointer_mints_new_key(self):
        request = self._request_with_session()
        first = get_or_create_preview_session_key(request, self.WEBAPP, self.USER)

        Session.objects.filter(session_key=first).update(
            expire_date=timezone.now() - timedelta(minutes=1)
        )

        second = get_or_create_preview_session_key(request, self.WEBAPP, self.USER)
        self.assertNotEqual(first, second)
        self.assertEqual(
            request.session[PREVIEW_KEYS_FIELD][str(self.WEBAPP.pk)], second
        )


@override_settings(WEBAPPS_DOMAIN=WEBAPPS_DOMAIN, ALLOWED_HOSTS=["*"])
class DevLocalViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("owner@test.com", "password")
        cls.OTHER_USER = User.objects.create_user("outsider@test.com", "password")
        cls.WORKSPACE = Workspace.objects.create(name="Dev WS", slug="dev-ws")
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.WEBAPP = Webapp.objects.create(
            name="Dev App",
            slug="dev-app",
            subdomain="dev-app",
            url="http://example.com",
            workspace=cls.WORKSPACE,
            created_by=cls.USER,
            is_public=False,
            type=Webapp.WebappType.STATIC,
            allowed_operations=[Webapp.OperationScope.USER_READ],
        )

    def _dev_auth_url(self, origin):
        return (
            f"/webapps/dev-auth/?workspaceSlug={self.WORKSPACE.slug}"
            f"&webappSlug={self.WEBAPP.slug}&origin={origin}"
        )

    def test_dev_js_served_anonymously(self):
        response = self.client.get("/webapps/dev.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn("javascript", response["Content-Type"])
        self.assertIn("OPENHEXA", response.content.decode())

    def test_dev_auth_requires_login(self):
        response = self.client.get(self._dev_auth_url("http://localhost:5173"))
        self.assertEqual(response.status_code, 302)

    def test_dev_auth_rejects_non_local_origin(self):
        self.client.force_login(self.USER)
        response = self.client.get(self._dev_auth_url("https://evil.com"))
        self.assertEqual(response.status_code, 400)

    def test_dev_auth_null_origin_shows_consent_without_minting(self):
        self.client.force_login(self.USER)
        response = self.client.get(self._dev_auth_url("null"))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Approve", content)
        self.assertNotIn(f".{WEBAPPS_DOMAIN}", content)

    def test_dev_auth_null_origin_mints_after_approval(self):
        self.client.force_login(self.USER)
        response = self.client.post(
            "/webapps/dev-auth/",
            {
                "workspaceSlug": self.WORKSPACE.slug,
                "webappSlug": self.WEBAPP.slug,
                "origin": "null",
            },
        )
        self.assertEqual(response.status_code, 200)

        preview_key = self.client.session[PREVIEW_KEYS_FIELD][str(self.WEBAPP.pk)]
        self.assertTrue(Session.objects.filter(session_key=preview_key).exists())
        self.assertIn(
            f"http://{preview_key}.{WEBAPPS_DOMAIN}/", response.content.decode()
        )

    def test_dev_auth_forbidden_without_access(self):
        self.client.force_login(self.OTHER_USER)
        response = self.client.get(self._dev_auth_url("http://localhost:5173"))
        self.assertEqual(response.status_code, 403)

    def test_dev_auth_no_webapp_shows_picker_without_minting(self):
        self.client.force_login(self.USER)
        response = self.client.get("/webapps/dev-auth/?origin=http://localhost:5173")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn(self.WORKSPACE.slug, content)
        self.assertIn(self.WEBAPP.slug, content)
        self.assertIn("Dev App", content)
        self.assertNotIn(f".{WEBAPPS_DOMAIN}", content)

    def test_dev_auth_picker_empty_for_user_without_webapps(self):
        self.client.force_login(self.OTHER_USER)
        response = self.client.get("/webapps/dev-auth/?origin=http://localhost:5173")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.WEBAPP.slug, response.content.decode())

    def test_dev_auth_pick_mints(self):
        self.client.force_login(self.USER)
        response = self.client.post(
            "/webapps/dev-auth/",
            {
                "workspaceSlug": self.WORKSPACE.slug,
                "webappSlug": self.WEBAPP.slug,
                "origin": "http://localhost:5173",
            },
        )
        self.assertEqual(response.status_code, 200)

        preview_key = self.client.session[PREVIEW_KEYS_FIELD][str(self.WEBAPP.pk)]
        self.assertTrue(Session.objects.filter(session_key=preview_key).exists())
        self.assertIn(
            f"http://{preview_key}.{WEBAPPS_DOMAIN}/", response.content.decode()
        )

    def test_dev_auth_returns_preview_url(self):
        self.client.force_login(self.USER)
        response = self.client.get(self._dev_auth_url("http://localhost:5173"))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn(f".{WEBAPPS_DOMAIN}", content)
        self.assertEqual(response["Content-Security-Policy"], "frame-ancestors 'none'")
        # The popup must keep its opener link to postMessage the result back,
        # so the default COOP (same-origin) must be overridden.
        self.assertEqual(response["Cross-Origin-Opener-Policy"], "unsafe-none")
