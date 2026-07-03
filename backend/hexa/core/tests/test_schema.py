from django.contrib.auth.password_validation import password_validators_help_texts
from django.test import override_settings

from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_airflow.models import (
    DAG,
    Cluster,
    DAGPermission,
    DAGTemplate,
)
from hexa.plugins.connector_postgresql.models import Database, DatabasePermission
from hexa.plugins.connector_s3.models import Bucket, BucketPermission, Object
from hexa.user_management.models import Membership, Team, User


class CoreDashboardTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )

        cls.TEAM_1 = Team.objects.create(name="Test Team 1")

        Membership.objects.create(user=cls.USER_SABRINA, team=cls.TEAM_1)

        cls.DB = Database.objects.create(
            hostname="host", username="user", password="pwd", database="db1"
        )

        DatabasePermission.objects.create(database=cls.DB, team=cls.TEAM_1)

        # S3 Bucket setup

        cls.BUCKET = Bucket.objects.create(name="test-bucket")
        cls.OBJECT = Object.objects.create(
            bucket=cls.BUCKET, key="file1.ipynb", size=100
        )

        BucketPermission.objects.create(bucket=cls.BUCKET, team=cls.TEAM_1)

        # DAG setup

        cluster = Cluster.objects.create(
            name="Test cluster 2", url="http://another-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        cls.DAG = DAG.objects.create(template=template, dag_id="Test DAG 1 ")

        DAGPermission.objects.create(dag=cls.DAG, team=cls.TEAM_1)

    def test_get_password_requirements_config(self):
        response = self.run_query(
            """
            query {
                config {
                    passwordRequirements
                }
            }
            """
        )

        self.assertEqual(
            response["data"]["config"]["passwordRequirements"],
            password_validators_help_texts(),
        )

    @override_settings(ASSISTANT_MANAGED=True)
    def test_assistant_managed_true(self):
        response = self.run_query("query { config { assistantManaged } }")
        self.assertTrue(response["data"]["config"]["assistantManaged"])

    @override_settings(ASSISTANT_MANAGED=False)
    def test_assistant_managed_false(self):
        response = self.run_query("query { config { assistantManaged } }")
        self.assertFalse(response["data"]["config"]["assistantManaged"])


_WHO_PROVIDER = {
    "id": "who",
    "display_name": "WHO",
    "client_id": "test-client-id",
    "client_secret": "test-secret",
    "server_url": "https://login.microsoftonline.com/test-tenant/v2.0",
}

_OIDC_QUERY = """
    query {
        config {
            oidcProviders {
                id
                displayName
                loginUrl
            }
        }
    }
"""


class OidcProvidersConfigTest(GraphQLTestCase):
    @override_settings(OIDC_PROVIDERS=[])
    def test_returns_empty_list_when_no_providers(self):
        response = self.run_query(_OIDC_QUERY)
        self.assertEqual(response["data"]["config"]["oidcProviders"], [])

    @override_settings(
        BASE_URL="http://app.example.com",
        OIDC_PROVIDERS=[_WHO_PROVIDER],
    )
    def test_returns_provider_with_correct_fields(self):
        response = self.run_query(_OIDC_QUERY)
        providers = response["data"]["config"]["oidcProviders"]
        self.assertEqual(len(providers), 1)
        self.assertEqual(providers[0]["id"], "who")
        self.assertEqual(providers[0]["displayName"], "WHO")
        self.assertEqual(
            providers[0]["loginUrl"],
            "http://app.example.com/accounts/oidc/who/login/",
        )

    @override_settings(
        BASE_URL="http://app.example.com",
        OIDC_PROVIDERS=[
            _WHO_PROVIDER,
            {**_WHO_PROVIDER, "id": "wfp", "display_name": "WFP"},
        ],
    )
    def test_returns_all_providers_in_order(self):
        response = self.run_query(_OIDC_QUERY)
        providers = response["data"]["config"]["oidcProviders"]
        self.assertEqual([p["id"] for p in providers], ["who", "wfp"])

    @override_settings(
        BASE_URL="http://app.example.com/",
        OIDC_PROVIDERS=[_WHO_PROVIDER],
    )
    def test_login_url_has_no_double_slash_when_base_url_has_trailing_slash(self):
        response = self.run_query(_OIDC_QUERY)
        login_url = response["data"]["config"]["oidcProviders"][0]["loginUrl"]
        self.assertNotIn("//accounts", login_url)
        self.assertEqual(login_url, "http://app.example.com/accounts/oidc/who/login/")
