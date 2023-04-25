import base64
import json
from unittest.mock import patch

from django.urls import reverse

from hexa.core.test import TestCase
from hexa.databases.api import get_db_server_credentials
from hexa.files.tests.mocks.mockgcp import mock_gcp_storage
from hexa.user_management.models import Feature, FeatureFlag, User
from hexa.workspaces.models import (
    Connection,
    ConnectionType,
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class ViewsTest(TestCase):
    @classmethod
    @mock_gcp_storage
    def setUpTestData(cls):
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
        )

        cls.USER_JULIA = User.objects.create_user(
            "julia@bluesquarehub.com", "juliaspassword"
        )

        cls.USER_REBECCA = User.objects.create_user(
            "rebecca@bluesquarehub.com",
            "standardpassword",
        )

        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces"), user=cls.USER_JULIA
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_JULIA,
            name="Senegal Workspace",
            description="This is a workspace for Senegal",
            countries=[{"code": "AL"}],
        )

        cls.WORKSPACE_MEMBERSHIP = WorkspaceMembership.objects.create(
            user=cls.USER_REBECCA,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.VIEWER,
        )

        cls.WORKSPACE_CONNECTION = Connection.objects.create_if_has_perm(
            cls.USER_JULIA,
            cls.WORKSPACE,
            name="DB",
            description="Connection's description",
            connection_type=ConnectionType.POSTGRESQL,
        )

        cls.WORKSPACE_CONNECTION.set_fields(
            cls.USER_JULIA,
            [
                {"code": "host", "secret": False, "value": "127.0.0.1"},
                {"code": "port", "secret": False, "value": "5432"},
                {"code": "username", "secret": False, "value": "hexa-app"},
                {"code": "password", "secret": True, "value": "hexa-app"},
                {"code": "db_name", "secret": False, "value": "hexa-app"},
            ],
        )

    def test_workspace_credentials_404(self):
        self.client.force_login(self.USER_JANE)
        response = self.client.post(
            reverse(
                "workspaces:credentials", kwargs={"workspace_slug": self.WORKSPACE.slug}
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_workspace_credentials_401(self):
        self.client.force_login(self.USER_REBECCA)
        response = self.client.post(
            reverse(
                "workspaces:credentials", kwargs={"workspace_slug": self.WORKSPACE.slug}
            )
        )
        self.assertEqual(response.status_code, 401)

    @patch(
        "hexa.files.credentials.get_short_lived_downscoped_access_token",
        return_value=("gcs-token", 3600),
    )
    def test_workspace_credentials_200(
        self, mock_get_short_lived_downscoped_access_token
    ):
        self.client.force_login(self.USER_JULIA)
        response = self.client.post(
            reverse(
                "workspaces:credentials", kwargs={"workspace_slug": self.WORKSPACE.slug}
            )
        )

        db_credentials = get_db_server_credentials()
        workspace_db_url = f"postgresql://{self.WORKSPACE.db_name}:{self.WORKSPACE.db_password}@{db_credentials['host']}:{db_credentials['port']}/{self.WORKSPACE.db_name}"

        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response_data["env"],
            {
                "DB_HOST": "127.0.0.1",
                "DB_PORT": "5432",
                "DB_USERNAME": "hexa-app",
                "DB_PASSWORD": "hexa-app",
                "DB_DATABASE": "hexa-app",  # Kept for backward-compat
                "DB_DB_NAME": "hexa-app",
                "DB_URL": "postgresql+psycopg2://hexa-app:hexa-app@127.0.0.1:5432/hexa-app",
                "WORKSPACE_DATABASE_DB_NAME": self.WORKSPACE.db_name,
                "WORKSPACE_DATABASE_HOST": db_credentials["host"],
                "WORKSPACE_DATABASE_PORT": db_credentials["port"],
                "WORKSPACE_DATABASE_USERNAME": self.WORKSPACE.db_name,
                "WORKSPACE_DATABASE_PASSWORD": self.WORKSPACE.db_password,
                "WORKSPACE_DATABASE_URL": workspace_db_url,
                "GCS_TOKEN": "gcs-token",
                "GCS_BUCKETS": base64.b64encode(
                    json.dumps(
                        {
                            "buckets": [
                                {
                                    "name": self.WORKSPACE.bucket_name,
                                    "mode": "RW",
                                    "mount": "/workspace",
                                }
                            ]
                        }
                    ).encode()
                ).decode(),
            },
        )
        self.assertEqual(
            response_data["notebooks_server_hash"],
            self.WORKSPACE.workspacemembership_set.get(
                user=self.USER_JULIA
            ).notebooks_server_hash,
        )
