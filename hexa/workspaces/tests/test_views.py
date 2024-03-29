from unittest.mock import patch

from django.core.signing import Signer
from django.urls import reverse

from hexa.core.test import TestCase
from hexa.databases.api import get_db_server_credentials
from hexa.files.tests.mocks.mockgcp import mock_gcp_storage
from hexa.pipelines.models import Pipeline, PipelineRunTrigger
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
            "julia@bluesquarehub.com", "juliaspassword", is_superuser=True
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

        cls.WORKSPACE_MEMBERSHIP_JULIA = WorkspaceMembership.objects.get(
            workspace=cls.WORKSPACE, user=cls.USER_JULIA
        )

        cls.WORKSPACE_MEMBERSHIP_REBECCA = WorkspaceMembership.objects.create(
            user=cls.USER_REBECCA,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.VIEWER,
        )

        cls.WORKSPACE_POSTGRESQL_CONNECTION = Connection.objects.create_if_has_perm(
            cls.USER_JULIA,
            cls.WORKSPACE,
            name="DB",
            description="Connection's description",
            connection_type=ConnectionType.POSTGRESQL,
        )

        cls.WORKSPACE_POSTGRESQL_CONNECTION.set_fields(
            cls.USER_JULIA,
            [
                {"code": "host", "value": "127.0.0.1"},
                {"code": "port", "value": "5432"},
                {"code": "username", "value": "hexa-app"},
                {"code": "password", "secret": True, "value": "hexa-app"},
                {"code": "db_name", "secret": False, "value": "hexa-app"},
            ],
        )

        cls.WORKSPACE_S3_CONNECTION = Connection.objects.create_if_has_perm(
            cls.USER_JULIA,
            cls.WORKSPACE,
            name="S3",
            description="S3 connection",
            connection_type=ConnectionType.S3,
        )

        cls.WORKSPACE_S3_CONNECTION.set_fields(
            cls.USER_JULIA,
            [
                {"code": "bucket_name", "value": "bucket_name"},
                {"code": "access_key_id", "value": "access_key"},
                {"code": "secret_access_key", "value": "hexa-app"},
            ],
        )

        cls.WORKSPACE_GCS_CONNECTION = Connection.objects.create_if_has_perm(
            cls.USER_JULIA,
            cls.WORKSPACE,
            name="GCS",
            description="GCS connection",
            connection_type=ConnectionType.GCS,
        )

        cls.WORKSPACE_GCS_CONNECTION.set_fields(
            cls.USER_JULIA,
            [
                {"code": "bucket_name", "value": "bucket_name"},
                {"code": "service_account_key", "value": "key"},
            ],
        )

        cls.WORKSPACE_IASO_CONNECTION = Connection.objects.create_if_has_perm(
            cls.USER_JULIA,
            cls.WORKSPACE,
            name="IASO",
            description="IASO connection",
            connection_type=ConnectionType.IASO,
        )

        cls.WORKSPACE_IASO_CONNECTION.set_fields(
            cls.USER_JULIA,
            [
                {"code": "url", "value": "url"},
                {"code": "username", "value": "user"},
                {"code": "password", "secret": True, "value": "admin"},
            ],
        )

        cls.WORKSPACE_DHIS2_CONNECTION = Connection.objects.create_if_has_perm(
            cls.USER_JULIA,
            cls.WORKSPACE,
            name="DHIS2",
            description="DHIS2 connection",
            connection_type=ConnectionType.DHIS2,
        )

        cls.WORKSPACE_DHIS2_CONNECTION.set_fields(
            cls.USER_JULIA,
            [
                {"code": "url", "value": "url"},
                {"code": "username", "value": "user"},
                {"code": "password", "secret": True, "value": "admin"},
            ],
        )

        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="Test pipeline",
            code="my-pipeline",
            description="This is a test pipeline",
        )
        cls.PIPELINE.upload_new_version(cls.USER_JULIA, b"", [])

    def test_workspace_credentials_404(self):
        self.client.force_login(self.USER_JANE)
        response = self.client.post(
            reverse("workspaces:credentials"),
            data={"workspace": self.WORKSPACE.slug},
        )
        self.assertEqual(response.status_code, 404)

    def test_workspace_credentials_anonymous(self):
        response = self.client.post(
            reverse("workspaces:credentials"),
            data={"workspace": self.WORKSPACE.slug},
        )
        self.assertEqual(response.status_code, 401)

    def test_credentials_no_workspace(self):
        response = self.client.post(
            reverse("workspaces:credentials"),
        )
        self.assertEqual(response.status_code, 400)

    def test_workspace_credentials_401(self):
        self.client.force_login(self.USER_REBECCA)
        response = self.client.post(
            reverse(
                "workspaces:credentials",
            ),
            data={"workspace": self.WORKSPACE.slug},
        )
        self.assertEqual(response.status_code, 401)

    @patch(
        "hexa.workspaces.views.get_short_lived_downscoped_access_token",
        return_value=("gcs-token", 3600, "gcp"),
    )
    def test_workspace_credentials_200(
        self, mock_get_short_lived_downscoped_access_token
    ):
        self.client.force_login(self.USER_JULIA)
        response = self.client.post(
            reverse("workspaces:credentials"),
            data={"workspace": self.WORKSPACE.slug},
        )

        db_credentials = get_db_server_credentials()

        self.maxDiff = None

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
                "DB_URL": "postgresql://hexa-app:hexa-app@127.0.0.1:5432/hexa-app",
                "WORKSPACE_BUCKET_NAME": self.WORKSPACE.bucket_name,
                "WORKSPACE_DATABASE_DB_NAME": self.WORKSPACE.db_name,
                "WORKSPACE_DATABASE_HOST": self.WORKSPACE.db_host,
                "WORKSPACE_DATABASE_PORT": db_credentials["port"],
                "WORKSPACE_DATABASE_USERNAME": self.WORKSPACE.db_name,
                "WORKSPACE_DATABASE_PASSWORD": self.WORKSPACE.db_password,
                "WORKSPACE_DATABASE_URL": self.WORKSPACE.db_url,
                "WORKSPACE_STORAGE_ENGINE": "gcp",
                "WORKSPACE_STORAGE_ENGINE_GCP_ACCESS_TOKEN": "gcs-token",
                "GCS_TOKEN": "gcs-token",
                "HEXA_TOKEN": Signer().sign_object(
                    self.WORKSPACE_MEMBERSHIP_JULIA.access_token
                ),
                "GCS_BUCKET_NAME": self.WORKSPACE_GCS_CONNECTION.fields.get(
                    code="bucket_name"
                ).value,
                "GCS_SERVICE_ACCOUNT_KEY": self.WORKSPACE_GCS_CONNECTION.fields.get(
                    code="service_account_key"
                ).value,
                "IASO_API_URL": self.WORKSPACE_IASO_CONNECTION.fields.get(
                    code="url"
                ).value,
                "IASO_URL": self.WORKSPACE_IASO_CONNECTION.fields.get(code="url").value,
                "IASO_USERNAME": self.WORKSPACE_IASO_CONNECTION.fields.get(
                    code="username"
                ).value,
                "IASO_PASSWORD": self.WORKSPACE_IASO_CONNECTION.fields.get(
                    code="password"
                ).value,
                "S3_ACCESS_KEY_ID": self.WORKSPACE_S3_CONNECTION.fields.get(
                    code="access_key_id"
                ).value,
                "S3_BUCKET_NAME": self.WORKSPACE_S3_CONNECTION.fields.get(
                    code="bucket_name"
                ).value,
                "S3_SECRET_ACCESS_KEY": self.WORKSPACE_S3_CONNECTION.fields.get(
                    code="secret_access_key"
                ).value,
                "DHIS2_API_URL": self.WORKSPACE_DHIS2_CONNECTION.fields.get(
                    code="url"
                ).value,
                "DHIS2_URL": self.WORKSPACE_DHIS2_CONNECTION.fields.get(
                    code="url"
                ).value,
                "DHIS2_USERNAME": self.WORKSPACE_DHIS2_CONNECTION.fields.get(
                    code="username"
                ).value,
                "DHIS2_PASSWORD": self.WORKSPACE_DHIS2_CONNECTION.fields.get(
                    code="password"
                ).value,
            },
        )
        self.assertEqual(
            response_data["notebooks_server_hash"],
            self.WORKSPACE.workspacemembership_set.get(
                user=self.USER_JULIA
            ).notebooks_server_hash,
        )

    @patch(
        "hexa.workspaces.views.get_short_lived_downscoped_access_token",
        return_value=("gcs-token", 3600, "gcp"),
    )
    def test_pipeline_invalid_credentials_404(
        self, mock_get_short_lived_downscoped_access_token
    ):
        run = self.PIPELINE.run(
            self.USER_JULIA, self.PIPELINE.last_version, PipelineRunTrigger.MANUAL, {}
        )
        response = self.client.post(
            reverse("workspaces:credentials"),
            data={"workspace": self.WORKSPACE.slug},
            **{
                "HTTP_Authorization": f"Bearer {Signer().sign_object(run.access_token + 'invalid')}"
            },
        )

        self.assertEqual(response.status_code, 404)

    @patch(
        "hexa.workspaces.views.get_short_lived_downscoped_access_token",
        return_value=("gcs-token", 3600, "gcp"),
    )
    def test_pipeline_credentials_200(
        self, mock_get_short_lived_downscoped_access_token
    ):
        run = self.PIPELINE.run(
            self.USER_JULIA, self.PIPELINE.last_version, PipelineRunTrigger.MANUAL, {}
        )
        token = Signer().sign_object(run.access_token)
        response = self.client.post(
            reverse("workspaces:credentials"),
            data={"workspace": self.WORKSPACE.slug},
            **{"HTTP_Authorization": f"Bearer {token}"},
        )

        db_credentials = get_db_server_credentials()

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
                "DB_URL": "postgresql://hexa-app:hexa-app@127.0.0.1:5432/hexa-app",
                "WORKSPACE_BUCKET_NAME": self.WORKSPACE.bucket_name,
                "WORKSPACE_DATABASE_DB_NAME": self.WORKSPACE.db_name,
                "WORKSPACE_DATABASE_HOST": self.WORKSPACE.db_host,
                "WORKSPACE_DATABASE_PORT": db_credentials["port"],
                "WORKSPACE_DATABASE_USERNAME": self.WORKSPACE.db_name,
                "WORKSPACE_DATABASE_PASSWORD": self.WORKSPACE.db_password,
                "WORKSPACE_DATABASE_URL": self.WORKSPACE.db_url,
                "WORKSPACE_STORAGE_ENGINE": "gcp",
                "WORKSPACE_STORAGE_ENGINE_GCP_ACCESS_TOKEN": "gcs-token",
                "GCS_TOKEN": "gcs-token",
                "HEXA_TOKEN": token,
                "GCS_BUCKET_NAME": self.WORKSPACE_GCS_CONNECTION.fields.get(
                    code="bucket_name"
                ).value,
                "GCS_SERVICE_ACCOUNT_KEY": self.WORKSPACE_GCS_CONNECTION.fields.get(
                    code="service_account_key"
                ).value,
                "IASO_API_URL": self.WORKSPACE_IASO_CONNECTION.fields.get(
                    code="url"
                ).value,
                "IASO_URL": self.WORKSPACE_IASO_CONNECTION.fields.get(code="url").value,
                "IASO_USERNAME": self.WORKSPACE_IASO_CONNECTION.fields.get(
                    code="username"
                ).value,
                "IASO_PASSWORD": self.WORKSPACE_IASO_CONNECTION.fields.get(
                    code="password"
                ).value,
                "S3_ACCESS_KEY_ID": self.WORKSPACE_S3_CONNECTION.fields.get(
                    code="access_key_id"
                ).value,
                "S3_BUCKET_NAME": self.WORKSPACE_S3_CONNECTION.fields.get(
                    code="bucket_name"
                ).value,
                "S3_SECRET_ACCESS_KEY": self.WORKSPACE_S3_CONNECTION.fields.get(
                    code="secret_access_key"
                ).value,
                "DHIS2_API_URL": self.WORKSPACE_DHIS2_CONNECTION.fields.get(
                    code="url"
                ).value,
                "DHIS2_URL": self.WORKSPACE_DHIS2_CONNECTION.fields.get(
                    code="url"
                ).value,
                "DHIS2_USERNAME": self.WORKSPACE_DHIS2_CONNECTION.fields.get(
                    code="username"
                ).value,
                "DHIS2_PASSWORD": self.WORKSPACE_DHIS2_CONNECTION.fields.get(
                    code="password"
                ).value,
            },
        )
        self.assertEqual(
            response_data["notebooks_server_hash"],
            str(run.id),
        )
