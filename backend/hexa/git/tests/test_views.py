import base64
from datetime import timedelta

from django.utils import timezone
from oauth2_provider.models import AccessToken, Application

from hexa.core.test import TestCase
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.webapps.models import GitWebapp, Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)

AUTHORIZE_URL = "/api/git/authorize"
REPO = "test-workspace-webapp-app"
ORG = "no-org"


class GitAuthMixin:
    """Shared token + request helpers for the git authorize view tests."""

    def _token(self, user, *, scope="openhexa:git", expired=False):
        delta = timedelta(hours=-1) if expired else timedelta(hours=1)
        return AccessToken.objects.create(
            user=user,
            application=self.application,
            token=f"tok-{user.email}-{scope}-{expired}",
            expires=timezone.now() + delta,
            scope=scope,
        ).token

    def _get(self, *, token=None, uri, method="GET", basic=False):
        headers = {"HTTP_X_ORIGINAL_URI": uri, "HTTP_X_ORIGINAL_METHOD": method}
        if token is not None:
            if basic:
                creds = base64.b64encode(f"oauth2:{token}".encode()).decode()
                headers["HTTP_AUTHORIZATION"] = f"Basic {creds}"
            else:
                headers["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        return self.client.get(AUTHORIZE_URL, **headers)


class GitAuthorizeViewTest(GitAuthMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.workspace = Workspace.objects.create(name="Test Workspace")

        cls.viewer = User.objects.create_user("viewer@bluesquarehub.com", "password")
        cls.editor = User.objects.create_user("editor@bluesquarehub.com", "password")
        cls.outsider = User.objects.create_user(
            "outsider@bluesquarehub.com", "password"
        )
        WorkspaceMembership.objects.create(
            user=cls.viewer,
            workspace=cls.workspace,
            role=WorkspaceMembershipRole.VIEWER,
        )
        WorkspaceMembership.objects.create(
            user=cls.editor,
            workspace=cls.workspace,
            role=WorkspaceMembershipRole.EDITOR,
        )
        cls.admin = User.objects.create_user("admin@bluesquarehub.com", "password")
        WorkspaceMembership.objects.create(
            user=cls.admin,
            workspace=cls.workspace,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.superuser = User.objects.create_user(
            "super@bluesquarehub.com", "password", is_superuser=True
        )

        cls.webapp = GitWebapp.objects.create(
            name="App",
            slug="app",
            subdomain="test-workspace-app",
            workspace=cls.workspace,
            created_by=cls.editor,
            type=Webapp.WebappType.STATIC,
            repository=REPO,
        )

        cls.application = Application.objects.create(
            name="git-client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )

    @staticmethod
    def _read_uri():
        return f"/{ORG}/{REPO}.git/info/refs?service=git-upload-pack"

    @staticmethod
    def _write_uri():
        return f"/{ORG}/{REPO}.git/info/refs?service=git-receive-pack"

    def test_missing_credentials_returns_401(self):
        response = self._get(uri=self._read_uri())
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("WWW-Authenticate", response)

    def test_unknown_token_returns_401(self):
        response = self._get(token="does-not-exist", uri=self._read_uri())
        self.assertEqual(response.status_code, 401)

    def test_expired_token_returns_401(self):
        token = self._token(self.viewer, expired=True)
        response = self._get(token=token, uri=self._read_uri())
        self.assertEqual(response.status_code, 401)

    def test_wrong_scope_returns_403(self):
        token = self._token(self.viewer, scope="openhexa:mcp")
        response = self._get(token=token, uri=self._read_uri())
        self.assertEqual(response.status_code, 403)

    def test_viewer_can_read(self):
        response = self._get(token=self._token(self.viewer), uri=self._read_uri())
        self.assertEqual(response.status_code, 200)

    def test_editor_can_read(self):
        response = self._get(token=self._token(self.editor), uri=self._read_uri())
        self.assertEqual(response.status_code, 200)

    def test_admin_can_read(self):
        response = self._get(token=self._token(self.admin), uri=self._read_uri())
        self.assertEqual(response.status_code, 200)

    def test_superuser_can_read(self):
        response = self._get(token=self._token(self.superuser), uri=self._read_uri())
        self.assertEqual(response.status_code, 200)

    def test_outsider_cannot_read(self):
        response = self._get(token=self._token(self.outsider), uri=self._read_uri())
        self.assertEqual(response.status_code, 403)

    def test_viewer_cannot_write(self):
        response = self._get(
            token=self._token(self.viewer), uri=self._write_uri(), method="POST"
        )
        self.assertEqual(response.status_code, 403)

    def test_editor_can_write(self):
        response = self._get(
            token=self._token(self.editor), uri=self._write_uri(), method="POST"
        )
        self.assertEqual(response.status_code, 200)

    def test_admin_can_write(self):
        response = self._get(
            token=self._token(self.admin), uri=self._write_uri(), method="POST"
        )
        self.assertEqual(response.status_code, 200)

    def test_superuser_can_write(self):
        response = self._get(
            token=self._token(self.superuser), uri=self._write_uri(), method="POST"
        )
        self.assertEqual(response.status_code, 200)

    def test_outsider_cannot_write(self):
        response = self._get(
            token=self._token(self.outsider), uri=self._write_uri(), method="POST"
        )
        self.assertEqual(response.status_code, 403)

    def test_basic_auth_token_as_password(self):
        token = self._token(self.viewer)
        response = self._get(token=token, uri=self._read_uri(), basic=True)
        self.assertEqual(response.status_code, 200)

    def test_unknown_repository_returns_403(self):
        token = self._token(self.editor)
        response = self._get(
            token=token,
            uri=f"/{ORG}/unknown-repo.git/info/refs?service=git-upload-pack",
        )
        self.assertEqual(response.status_code, 403)

    def test_org_mismatch_returns_403(self):
        token = self._token(self.editor)
        response = self._get(
            token=token,
            uri=f"/other-org/{REPO}.git/info/refs?service=git-upload-pack",
        )
        self.assertEqual(response.status_code, 403)

    def test_non_git_operation_is_blocked(self):
        # Even an editor (who can write) is denied a non clone/fetch/push path:
        # the proxy only forwards git smart-HTTP, not Forgejo's UI/API/LFS.
        token = self._token(self.editor)
        for uri in (
            f"/{ORG}/{REPO}.git/info/lfs/objects/batch",
            f"/{ORG}/{REPO}/settings",
            f"/{ORG}/{REPO}.git/HEAD",
        ):
            response = self._get(token=token, uri=uri)
            self.assertEqual(response.status_code, 403, uri)


class GitAuthorizeOrgPermissionsTest(GitAuthMixin, TestCase):
    """Org OWNER/ADMIN get read+write on org repos without workspace membership;
    plain org MEMBERs get nothing.
    """

    ORG_REPO = "org-workspace-webapp-app"

    @classmethod
    def setUpTestData(cls):
        cls.organization = Organization.objects.create(
            name="Test Org",
            short_name="test-org",
            organization_type="CORPORATE",
        )
        cls.workspace = Workspace.objects.create(
            name="Org Workspace", organization=cls.organization
        )

        cls.owner = User.objects.create_user("owner@bluesquarehub.com", "password")
        cls.org_admin = User.objects.create_user("oadmin@bluesquarehub.com", "password")
        cls.member = User.objects.create_user("member@bluesquarehub.com", "password")
        for user, role in (
            (cls.owner, OrganizationMembershipRole.OWNER),
            (cls.org_admin, OrganizationMembershipRole.ADMIN),
            (cls.member, OrganizationMembershipRole.MEMBER),
        ):
            OrganizationMembership.objects.create(
                organization=cls.organization, user=user, role=role
            )

        cls.webapp = GitWebapp.objects.create(
            name="Org App",
            slug="org-app",
            subdomain="org-workspace-app",
            workspace=cls.workspace,
            created_by=cls.owner,
            type=Webapp.WebappType.STATIC,
            repository=cls.ORG_REPO,
        )

        cls.application = Application.objects.create(
            name="git-client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )

    def _read_uri(self):
        return f"/{self.organization.slug}/{self.ORG_REPO}.git/info/refs?service=git-upload-pack"

    def _write_uri(self):
        return f"/{self.organization.slug}/{self.ORG_REPO}.git/info/refs?service=git-receive-pack"

    def test_org_owner_can_read_and_write(self):
        token = self._token(self.owner)
        self.assertEqual(self._get(token=token, uri=self._read_uri()).status_code, 200)
        self.assertEqual(
            self._get(token=token, uri=self._write_uri(), method="POST").status_code,
            200,
        )

    def test_org_admin_can_read_and_write(self):
        token = self._token(self.org_admin)
        self.assertEqual(self._get(token=token, uri=self._read_uri()).status_code, 200)
        self.assertEqual(
            self._get(token=token, uri=self._write_uri(), method="POST").status_code,
            200,
        )

    def test_org_member_has_no_access(self):
        token = self._token(self.member)
        self.assertEqual(self._get(token=token, uri=self._read_uri()).status_code, 403)
        self.assertEqual(
            self._get(token=token, uri=self._write_uri(), method="POST").status_code,
            403,
        )
