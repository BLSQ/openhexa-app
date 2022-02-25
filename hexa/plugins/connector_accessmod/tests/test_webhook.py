from urllib.parse import urljoin

import responses
from django import test
from django.urls import reverse

from hexa.plugins.connector_airflow.models import DAG, Cluster, DAGTemplate
from hexa.user_management.models import User


class AccessmodViewsTest(test.TestCase):
    @classmethod
    @responses.activate
    def setUpTestData(cls):
        cls.USER_TAYLOR = User.objects.create_user(
            "taylor@bluesquarehub.com",
            "taylorrocks66",
            is_superuser=True,
        )
        cls.CLUSTER = Cluster.objects.create(
            name="Test cluster", url="https://one-cluster-url.com"
        )
        cls.TEMPLATE = DAGTemplate.objects.create(cluster=cls.CLUSTER, code="TEST")
        cls.DAG = DAG.objects.create(template=cls.TEMPLATE, dag_id="test_dag")

        responses.add(
            responses.POST,
            urljoin(cls.CLUSTER.api_url, f"dags/{cls.DAG.dag_id}/dagRuns"),
            json={
                "conf": {},
                "dag_id": "test_dag",
                "dag_run_id": "test_dag_run_1",
                "end_date": "2021-10-09T16:42:16.189200+00:00",
                "execution_date": "2021-10-09T16:41:00+00:00",
                "external_trigger": False,
                "start_date": "2021-10-09T16:42:00.830209+00:00",
                "state": "queued",
            },
            status=200,
        )
        cls.DAG_RUN = cls.DAG.run(user=cls.USER_TAYLOR)

    def test_webhook_not_authenticated_401(self):
        response = self.client.post(
            reverse(
                "connector_accessmod:webhook",
            ),
            {"foo": "bar"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {"success": False},
        )

    def test_webhook_200(self):
        response = self.client.post(
            reverse(
                "connector_accessmod:webhook",
            ),
            {"foo": "bar"},
            **{"HTTP_AUTHORIZATION": f"Bearer {self.DAG_RUN.sign_webhook_token()}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": True},
        )
