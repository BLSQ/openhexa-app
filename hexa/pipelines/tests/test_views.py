from urllib.parse import urljoin

import responses
from django import test
from django.urls import reverse
from django.utils import timezone

from hexa.plugins.connector_airflow.models import DAG, Cluster, DAGRun, DAGRunState
from hexa.plugins.connector_airflow.tests.responses import (
    dag_run_hello_world_1,
    dag_run_hello_world_2,
)
from hexa.user_management.models import User


class ViewsTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
            is_superuser=True,
        )

    def test_index_200(self):
        cluster_1 = Cluster.objects.create(
            name="Test cluster 1 ", url="http://one-cluster-url.com"
        )
        cluster_2 = Cluster.objects.create(
            name="Test cluster 2", url="http://another-cluster-url.com"
        )
        dag_1 = DAG.objects.create(cluster=cluster_1, dag_id="Test DAG 1 ")
        dag_2 = DAG.objects.create(cluster=cluster_2, dag_id="Test DAG 2")
        DAGRun.objects.create(dag=dag_1, execution_date=timezone.now())
        DAGRun.objects.create(dag=dag_1, execution_date=timezone.now())
        DAGRun.objects.create(dag=dag_2, execution_date=timezone.now())

        self.client.force_login(self.USER_JANE)
        response = self.client.get(
            reverse(
                "pipelines:index",
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, len(response.context["environment_grid"]))
        self.assertEqual(3, len(response.context["run_grid"]))

    @responses.activate
    def test_index_refresh_200(self):
        cluster = Cluster.objects.create(
            name="Test cluster", url="https://one-cluster-url.com"
        )
        dag = DAG.objects.create(cluster=cluster, dag_id="hello_world")
        DAGRun.objects.create(
            dag=dag,
            run_id="hello_world_run_1",
            execution_date=timezone.now(),
            state=DAGRunState.RUNNING,
        )
        DAGRun.objects.create(
            dag=dag,
            run_id="hello_world_run_2",
            execution_date=timezone.now(),
            state=DAGRunState.RUNNING,
        )

        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "dags/hello_world/dagRuns/hello_world_run_1"),
            json=dag_run_hello_world_1,
            status=200,
        )
        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "dags/hello_world/dagRuns/hello_world_run_2"),
            json=dag_run_hello_world_2,
            status=200,
        )

        self.client.force_login(self.USER_JANE)
        response = self.client.get(
            reverse(
                "pipelines:index_refresh",
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, len(responses.calls))
        self.assertEqual(1, len(response.context["environment_grid"]))
        self.assertEqual(2, len(response.context["run_grid"]))

    @responses.activate
    def test_index_refresh_200_even_if_airflow_fails(self):
        cluster = Cluster.objects.create(
            name="Test cluster", url="https://one-cluster-url.com"
        )
        dag = DAG.objects.create(cluster=cluster, dag_id="hello_world")
        DAGRun.objects.create(
            dag=dag,
            run_id="hello_world_run_1",
            execution_date=timezone.now(),
            state=DAGRunState.RUNNING,
        )

        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "dags/hello_world/dagRuns/hello_world_run_1"),
            json={},
            status=404,
        )

        self.client.force_login(self.USER_JANE)
        with self.assertLogs("hexa.pipelines.views", level="ERROR") as cm:
            response = self.client.get(
                reverse(
                    "pipelines:index_refresh",
                ),
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(1, len(responses.calls))
        self.assertIn("Refresh failed for DAGRun", cm.output[0])
