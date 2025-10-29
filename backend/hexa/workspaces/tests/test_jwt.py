from unittest.mock import patch

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.test import override_settings

from hexa.core.test import GraphQLTestCase, TestCase
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.jwt_utils import (
    JWTConfigurationError,
    generate_workspace_jwt,
    load_private_key,
)
from hexa.workspaces.models import Workspace, WorkspaceMembership


def generate_test_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


class JWTUtilsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.private_key_pem, cls.public_key_pem = generate_test_key_pair()
        cls.USER_ALICE = User.objects.create_user(
            "alice@example.com",
            "password123",
        )

    @override_settings(OPENHEXA_JWT_PRIVATE_KEY=None)
    def test_load_private_key_not_configured(self):
        result = load_private_key()
        self.assertIsNone(result)

    def test_load_private_key_valid(self):
        with override_settings(OPENHEXA_JWT_PRIVATE_KEY=self.private_key_pem.decode()):
            result = load_private_key()
            self.assertIsNotNone(result)

    @override_settings(OPENHEXA_JWT_PRIVATE_KEY="invalid-key-data")
    def test_load_private_key_invalid(self):
        with self.assertRaises(JWTConfigurationError):
            load_private_key()

    def test_generate_workspace_jwt_success(self):
        with override_settings(
            OPENHEXA_JWT_PRIVATE_KEY=self.private_key_pem.decode(),
            OPENHEXA_JWT_ISSUER="https://test.openhexa.org",
            OPENHEXA_JWT_AUDIENCE="test-clients",
            OPENHEXA_JWT_TTL=3600,
        ):
            result = generate_workspace_jwt(
                user_id="user-123",
                user_email="alice@example.com",
                workspace_id="workspace-abc",
                workspace_slug="test-workspace",
                role="EDITOR",
            )

            self.assertIn("token", result)
            self.assertIn("expires_at", result)

            decoded = jwt.decode(
                result["token"],
                self.public_key_pem,
                algorithms=["RS256"],
                audience="test-clients",
                issuer="https://test.openhexa.org",
            )

            self.assertEqual(decoded["sub"], "user-123")
            self.assertEqual(decoded["iss"], "https://test.openhexa.org")
            self.assertEqual(decoded["aud"], "test-clients")
            self.assertEqual(
                decoded["https://app.openhexa.org/claims/workspace"]["id"],
                "workspace-abc",
            )
            self.assertEqual(
                decoded["https://app.openhexa.org/claims/workspace"]["slug"],
                "test-workspace",
            )
            self.assertEqual(
                decoded["https://app.openhexa.org/claims/workspace_role"], "EDITOR"
            )
            self.assertEqual(
                decoded["https://app.openhexa.org/claims/user"]["id"], "user-123"
            )
            self.assertEqual(
                decoded["https://app.openhexa.org/claims/user"]["email"],
                "alice@example.com",
            )
            self.assertIn("jti", decoded)
            self.assertIn("iat", decoded)
            self.assertIn("exp", decoded)

    def test_generate_workspace_jwt_with_kid(self):
        with override_settings(
            OPENHEXA_JWT_PRIVATE_KEY=self.private_key_pem.decode(),
            OPENHEXA_JWT_KID="test-key-id",
        ):
            result = generate_workspace_jwt(
                user_id="user-123",
                user_email="alice@example.com",
                workspace_id="workspace-abc",
                workspace_slug="test-workspace",
                role="VIEWER",
            )

            header = jwt.get_unverified_header(result["token"])
            self.assertEqual(header["kid"], "test-key-id")
            self.assertEqual(header["alg"], "RS256")
            self.assertEqual(header["typ"], "JWT")

    @override_settings(OPENHEXA_JWT_PRIVATE_KEY=None)
    def test_generate_workspace_jwt_no_key(self):
        with self.assertRaises(JWTConfigurationError) as context:
            generate_workspace_jwt(
                user_id="user-123",
                user_email="alice@example.com",
                workspace_id="workspace-abc",
                workspace_slug="test-workspace",
                role="EDITOR",
            )
        self.assertIn("not configured", str(context.exception))

    def test_generate_workspace_jwt_custom_ttl(self):
        with override_settings(
            OPENHEXA_JWT_PRIVATE_KEY=self.private_key_pem.decode(),
            OPENHEXA_JWT_ISSUER="https://test.openhexa.org",
            OPENHEXA_JWT_AUDIENCE="test-clients",
        ):
            result = generate_workspace_jwt(
                user_id="user-123",
                user_email="alice@example.com",
                workspace_id="workspace-abc",
                workspace_slug="test-workspace",
                role="EDITOR",
                ttl_seconds=7200,
            )

            decoded = jwt.decode(
                result["token"],
                self.public_key_pem,
                algorithms=["RS256"],
                audience="test-clients",
                issuer="https://test.openhexa.org",
                options={"verify_signature": True},
            )

            self.assertEqual(decoded["exp"] - decoded["iat"], 7200)


class IssueWorkspaceTokenMutationTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.private_key_pem, cls.public_key_pem = generate_test_key_pair()

        cls.USER_ALICE = User.objects.create_user(
            "alice@example.com",
            "password123",
        )
        cls.USER_BOB = User.objects.create_user(
            "bob@example.com",
            "password456",
        )

        cls.ORG = Organization.objects.create(name="Test Org")
        OrganizationMembership.objects.create(
            user=cls.USER_ALICE,
            organization=cls.ORG,
            role=OrganizationMembershipRole.ADMIN,
        )

        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            cls.WORKSPACE = Workspace.objects.create_if_has_perm(
                cls.USER_ALICE,
                name="Test Workspace",
                description="Test workspace for JWT",
                organization=cls.ORG,
            )

        cls.MEMBERSHIP_ALICE = WorkspaceMembership.objects.get(
            user=cls.USER_ALICE, workspace=cls.WORKSPACE
        )

    def test_issue_token_success_with_workspace_slug(self):
        with override_settings(
            OPENHEXA_JWT_PRIVATE_KEY=self.private_key_pem.decode(),
        ):
            self.client.force_login(self.USER_ALICE)
            r = self.run_query(
                """
                mutation issueToken($input: IssueWorkspaceTokenInput!) {
                    issueWorkspaceToken(input: $input) {
                        success
                        token
                        expiresAt
                        workspace {
                            id
                            slug
                        }
                        role
                        errors
                    }
                }
                """,
                {"input": {"workspaceSlug": self.WORKSPACE.slug}},
            )

            self.assertEqual(r["data"]["issueWorkspaceToken"]["success"], True)
            self.assertIsNotNone(r["data"]["issueWorkspaceToken"]["token"])
            self.assertIsNotNone(r["data"]["issueWorkspaceToken"]["expiresAt"])
            self.assertEqual(
                r["data"]["issueWorkspaceToken"]["workspace"]["slug"],
                self.WORKSPACE.slug,
            )
            self.assertEqual(r["data"]["issueWorkspaceToken"]["role"], "ADMIN")
            self.assertEqual(r["data"]["issueWorkspaceToken"]["errors"], [])

            token = r["data"]["issueWorkspaceToken"]["token"]
            decoded = jwt.decode(
                token,
                self.public_key_pem,
                algorithms=["RS256"],
                audience="openhexa-clients",
                issuer="https://app.openhexa.org",
                options={"verify_signature": True},
            )
            self.assertEqual(decoded["sub"], str(self.USER_ALICE.id))

    def test_issue_token_success_with_workspace_id(self):
        with override_settings(
            OPENHEXA_JWT_PRIVATE_KEY=self.private_key_pem.decode(),
        ):
            self.client.force_login(self.USER_ALICE)
            r = self.run_query(
                """
                mutation issueToken($input: IssueWorkspaceTokenInput!) {
                    issueWorkspaceToken(input: $input) {
                        success
                        token
                        workspace {
                            id
                            slug
                        }
                        role
                        errors
                    }
                }
                """,
                {"input": {"workspaceId": str(self.WORKSPACE.id)}},
            )

            self.assertEqual(r["data"]["issueWorkspaceToken"]["success"], True)
            self.assertIsNotNone(r["data"]["issueWorkspaceToken"]["token"])

    def test_issue_token_unauthenticated(self):
        r = self.run_query(
            """
            mutation issueToken($input: IssueWorkspaceTokenInput!) {
                issueWorkspaceToken(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"workspaceSlug": self.WORKSPACE.slug}},
        )

        self.assertIsNone(r.get("data"))
        self.assertIn("errors", r)

    def test_issue_token_invalid_input_both_provided(self):
        with override_settings(
            OPENHEXA_JWT_PRIVATE_KEY=self.private_key_pem.decode(),
        ):
            self.client.force_login(self.USER_ALICE)
            r = self.run_query(
                """
                mutation issueToken($input: IssueWorkspaceTokenInput!) {
                    issueWorkspaceToken(input: $input) {
                        success
                        errors
                    }
                }
                """,
                {
                    "input": {
                        "workspaceId": str(self.WORKSPACE.id),
                        "workspaceSlug": self.WORKSPACE.slug,
                    }
                },
            )

            self.assertEqual(r["data"]["issueWorkspaceToken"]["success"], False)
            self.assertIn("INPUT_INVALID", r["data"]["issueWorkspaceToken"]["errors"])

    def test_issue_token_invalid_input_none_provided(self):
        with override_settings(
            OPENHEXA_JWT_PRIVATE_KEY=self.private_key_pem.decode(),
        ):
            self.client.force_login(self.USER_ALICE)
            r = self.run_query(
                """
                mutation issueToken($input: IssueWorkspaceTokenInput!) {
                    issueWorkspaceToken(input: $input) {
                        success
                        errors
                    }
                }
                """,
                {"input": {}},
            )

            self.assertEqual(r["data"]["issueWorkspaceToken"]["success"], False)
            self.assertIn("INPUT_INVALID", r["data"]["issueWorkspaceToken"]["errors"])

    def test_issue_token_workspace_not_found(self):
        with override_settings(
            OPENHEXA_JWT_PRIVATE_KEY=self.private_key_pem.decode(),
        ):
            self.client.force_login(self.USER_ALICE)
            r = self.run_query(
                """
                mutation issueToken($input: IssueWorkspaceTokenInput!) {
                    issueWorkspaceToken(input: $input) {
                        success
                        errors
                    }
                }
                """,
                {"input": {"workspaceSlug": "non-existent-workspace"}},
            )

            self.assertEqual(r["data"]["issueWorkspaceToken"]["success"], False)
            self.assertIn(
                "WORKSPACE_NOT_FOUND", r["data"]["issueWorkspaceToken"]["errors"]
            )

    def test_issue_token_membership_required(self):
        with override_settings(
            OPENHEXA_JWT_PRIVATE_KEY=self.private_key_pem.decode(),
        ):
            self.client.force_login(self.USER_BOB)
            r = self.run_query(
                """
                mutation issueToken($input: IssueWorkspaceTokenInput!) {
                    issueWorkspaceToken(input: $input) {
                        success
                        errors
                    }
                }
                """,
                {"input": {"workspaceSlug": self.WORKSPACE.slug}},
            )

            self.assertEqual(r["data"]["issueWorkspaceToken"]["success"], False)
            self.assertIn(
                "MEMBERSHIP_REQUIRED", r["data"]["issueWorkspaceToken"]["errors"]
            )

    @override_settings(OPENHEXA_JWT_PRIVATE_KEY=None)
    def test_issue_token_missing_private_key(self):
        self.client.force_login(self.USER_ALICE)
        r = self.run_query(
            """
            mutation issueToken($input: IssueWorkspaceTokenInput!) {
                issueWorkspaceToken(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"workspaceSlug": self.WORKSPACE.slug}},
        )

        self.assertEqual(r["data"]["issueWorkspaceToken"]["success"], False)
        self.assertIn(
            "CONFIG_MISSING_PRIVATE_KEY", r["data"]["issueWorkspaceToken"]["errors"]
        )
