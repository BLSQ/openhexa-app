from unittest.mock import patch

from django.urls import reverse

from hexa.core.test import TestCase
from hexa.plugins.connector_airflow.models import DAG, Cluster, DAGTemplate
from hexa.user_management.models import User


class BaseCredentialsTestCase(TestCase):
    """
    Base class that provides a cluster, dag templte and dag
    so CredentialsTestCases in connectors can inherit from it
    """

    def setUp(self) -> None:
        self.maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
            is_superuser=True,
        )

        cls.CLUSTER = Cluster.objects.create(
            name="Test cluster 1 ", url="http://one-cluster-url.com"
        )
        cls.TEMPLATE = DAGTemplate.objects.create(cluster=cls.CLUSTER, code="TEST")
        cls.PIPELINE = DAG.objects.create(template=cls.TEMPLATE, dag_id="Test DAG 1")


def get_hexa_app_configs(connector_only=False):
    class AppConfig:
        def get_pipelines_credentials(self):
            def credentials_function(pipeline_credentials):
                pipeline_credentials.env["PIPELINE_ID"] = "a"

            return [credentials_function]

    return [AppConfig()]


class CredentialsTestCase(BaseCredentialsTestCase):
    @patch(
        "hexa.pipelines.views.get_hexa_app_configs",
        return_value=get_hexa_app_configs(),
    )
    def test_p2_credentials_200(self, _):
        token = self.PIPELINE.get_token()

        class AppConfig:
            def get_pipelines_credentials(self):
                def credentials_function(pipeline_credentials):
                    pipeline_credentials.env[
                        "TEST_PIPELINE_ID"
                    ] = pipeline_credentials.pipeline.id

                return [credentials_function]

        fake = [AppConfig()]

        with patch("hexa.pipelines.views.get_hexa_app_configs", return_value=fake):
            response = self.client.post(
                reverse(
                    "pipelines:credentials",
                ),
                **{"HTTP_AUTHORIZATION": f"Bearer {token}"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "env": {
                    "TEST_PIPELINE_ID": str(self.PIPELINE.pk),
                },
                "files": {},
            },
        )

    def test_credentials_401(self):
        response = self.client.post(reverse("pipelines:credentials"))

        self.assertEqual(response.status_code, 401)
        response_data = response.json()
        self.assertIn("error", response_data)
