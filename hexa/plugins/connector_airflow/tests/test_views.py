import json
from datetime import timedelta
from urllib.parse import urljoin

import responses
from django import test
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import ERROR
from django.urls import reverse
from django.utils import timezone

from hexa.plugins.connector_airflow.datacards import ClusterCard, DAGCard, DAGRunCard
from hexa.plugins.connector_airflow.models import (
    DAG,
    Cluster,
    DAGRun,
    DAGRunState,
    DAGTemplate,
)
from hexa.plugins.connector_airflow.tests.responses import (
    dag_run_hello_world_1,
    dag_run_same_old_1,
    dag_runs_hello_world,
    dag_runs_same_old,
    dags,
)
from hexa.user_management.models import User


class ViewsTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_TAYLOR = User.objects.create_user(
            "taylor@bluesquarehub.com",
            "taylorrocks66",
            is_superuser=True,
        )
        cls.USER_JIM = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jim44",
            is_superuser=True,
        )

    def test_cluster_detail_200(self):
        cluster = Cluster.objects.create(
            name="Test cluster", url="https://one-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        DAG.objects.create(template=template, dag_id="Test DAG 1")
        DAG.objects.create(template=template, dag_id="Test DAG 2")

        self.client.force_login(self.USER_TAYLOR)
        response = self.client.get(
            reverse(
                "connector_airflow:cluster_detail", kwargs={"cluster_id": cluster.id}
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["cluster_card"], ClusterCard)
        self.assertEqual(2, len(response.context["dag_grid"]))

    @responses.activate
    def test_cluster_detail_refresh_200(self):
        cluster = Cluster.objects.create(
            name="Test cluster", url="https://one-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        dag = DAG.objects.create(template=template, dag_id="hello_world")
        dag_run = DAGRun.objects.create(
            dag=dag,
            run_id="hello_world_run_1",
            execution_date=timezone.now(),
            state=DAGRunState.RUNNING,
        )

        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "dags/hello_world/dagRuns/hello_world_run_1"),
            json=dag_run_hello_world_1,
            status=200,
        )

        self.client.force_login(self.USER_TAYLOR)
        response = self.client.get(
            reverse(
                "connector_airflow:cluster_detail_refresh",
                kwargs={"cluster_id": cluster.id},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, len(responses.calls))
        dag_run.refresh_from_db()
        self.assertEqual(dag_run.state, DAGRunState.SUCCESS)
        self.assertIsInstance(response.context["cluster_card"], ClusterCard)

    @responses.activate
    def test_cluster_detail_refresh_200_even_if_airflow_fails(self):
        cluster = Cluster.objects.create(
            name="Old rusty cluster", url="https://old-rusty-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        dag = DAG.objects.create(template=template, dag_id="hello_world")
        DAGRun.objects.create(
            dag=dag,
            run_id="hello_world_run_2",
            execution_date=timezone.now(),
            state=DAGRunState.RUNNING,
        )

        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "dags/hello_world/dagRuns/hello_world_run_2"),
            json={},
            status=404,
        )

        self.client.force_login(self.USER_TAYLOR)
        with self.assertLogs(
            "hexa.plugins.connector_airflow.views", level="ERROR"
        ) as cm:
            response = self.client.get(
                reverse(
                    "connector_airflow:cluster_detail_refresh",
                    kwargs={"cluster_id": cluster.id},
                ),
            )
            self.assertEqual(response.status_code, 200)
        self.assertIn("Refresh failed for DAGRun", cm.output[0])

    def test_dag_detail_200(self):
        cluster = Cluster.objects.create(
            name="Test cluster", url="https://one-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        dag = DAG.objects.create(template=template, dag_id="Test DAG")
        DAGRun.objects.create(dag=dag, execution_date=timezone.now())
        DAGRun.objects.create(dag=dag, execution_date=timezone.now())

        self.client.force_login(self.USER_TAYLOR)
        response = self.client.get(
            reverse(
                "connector_airflow:dag_detail",
                kwargs={"dag_id": dag.id},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["dag_card"], DAGCard)
        self.assertEqual(2, len(response.context["run_grid"]))

    @responses.activate
    def test_dag_detail_refresh_200(self):
        cluster = Cluster.objects.create(
            name="Ok test cluster", url="https://ok-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        dag = DAG.objects.create(template=template, dag_id="same_old")
        dag_run = DAGRun.objects.create(
            dag=dag,
            run_id="same_old_run_1",
            execution_date=timezone.now(),
            state=DAGRunState.QUEUED,
        )

        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "dags/same_old/dagRuns/same_old_run_1"),
            json=dag_run_same_old_1,
            status=200,
        )

        self.client.force_login(self.USER_TAYLOR)
        response = self.client.get(
            reverse(
                "connector_airflow:dag_detail_refresh",
                kwargs={"dag_id": dag.id},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, len(responses.calls))
        dag_run.refresh_from_db()
        self.assertEqual(dag_run.state, DAGRunState.SUCCESS)
        self.assertIsInstance(response.context["dag_card"], DAGCard)

    @responses.activate
    def test_dag_detail_refresh_200_even_if_airflow_fails(self):
        cluster = Cluster.objects.create(
            name="Unstable Test cluster", url="https://unstable-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        dag = DAG.objects.create(template=template, dag_id="same_old")
        DAGRun.objects.create(
            dag=dag,
            run_id="same_old_run_1",
            execution_date=timezone.now(),
            state=DAGRunState.QUEUED,
        )

        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "dags/same_old/dagRuns/same_old_run_1"),
            json=dag_run_same_old_1,
            status=404,
        )

        self.client.force_login(self.USER_JIM)
        with self.assertLogs(
            "hexa.plugins.connector_airflow.views", level="ERROR"
        ) as cm:
            response = self.client.get(
                reverse(
                    "connector_airflow:dag_detail_refresh",
                    kwargs={"dag_id": dag.id},
                ),
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                DAGRunState.QUEUED, DAGRun.objects.get(run_id="same_old_run_1").state
            )
            self.assertEqual(1, len(responses.calls))
        self.assertIn("Refresh failed for DAGRun", cm.output[0])

    def test_dag_run_detail_200(self):
        cluster = Cluster.objects.create(
            name="Perfectly fine test cluster", url="https://fine-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        dag = DAG.objects.create(template=template, dag_id="same_old")
        dag_run = DAGRun.objects.create(
            dag=dag,
            run_id="same_old_run_1",
            execution_date=timezone.now() - timedelta(days=1),
            state=DAGRunState.SUCCESS,
        )

        self.client.force_login(self.USER_TAYLOR)
        response = self.client.get(
            reverse(
                "connector_airflow:dag_run_detail",
                kwargs={
                    "dag_id": dag.id,
                    "dag_run_id": dag_run.id,
                },
            ),
        )
        self.assertEqual(200, response.status_code)
        self.assertIsInstance(response.context["dag_run_card"], DAGRunCard)

    @responses.activate
    def test_dag_run_detail_refresh_200(self):
        cluster = Cluster.objects.create(
            name="Great test cluster", url="https://great-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        dag = DAG.objects.create(template=template, dag_id="same_old")
        dag_run = DAGRun.objects.create(
            dag=dag,
            run_id="same_old_run_1",
            execution_date=timezone.now() - timedelta(days=1),
            state=DAGRunState.QUEUED,
        )

        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "dags/same_old/dagRuns/same_old_run_1"),
            json=dag_run_same_old_1,
            status=200,
        )

        self.client.force_login(self.USER_TAYLOR)
        response = self.client.get(
            reverse(
                "connector_airflow:dag_run_detail_refresh",
                kwargs={
                    "dag_id": dag.id,
                    "dag_run_id": dag_run.id,
                },
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, len(responses.calls))
        dag_run.refresh_from_db()
        self.assertEqual(dag_run.state, DAGRunState.SUCCESS)
        self.assertIsInstance(response.context["dag_run_card"], DAGRunCard)

    @responses.activate
    def test_dag_run_detail_refresh_200_even_if_airflow_fails(self):
        cluster = Cluster.objects.create(
            name="Terrible Test cluster", url="https://terrible-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        dag = DAG.objects.create(template=template, dag_id="hello_world")
        dag_run = DAGRun.objects.create(
            dag=dag,
            run_id="hello_world_run_1",
            execution_date=timezone.now(),
            state=DAGRunState.QUEUED,
        )

        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "dags/hello_world/dagRuns/hello_world_run_1"),
            json=dag_run_hello_world_1,
            status=404,
        )

        self.client.force_login(self.USER_TAYLOR)
        with self.assertLogs(
            "hexa.plugins.connector_airflow.views", level="ERROR"
        ) as cm:
            response = self.client.get(
                reverse(
                    "connector_airflow:dag_run_detail_refresh",
                    kwargs={
                        "dag_id": dag.id,
                        "dag_run_id": dag_run.id,
                    },
                ),
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                DAGRunState.QUEUED, DAGRun.objects.get(run_id="hello_world_run_1").state
            )
            self.assertEqual(1, len(responses.calls))
        self.assertIn("Refresh failed for DAGRun", cm.output[0])

    @responses.activate
    @test.override_settings(AIRFLOW_SYNC_WAIT=0.1)
    def test_sync_302(self):
        cluster = Cluster.objects.create(
            name="Test cluster", url="https://one-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        DAG.objects.create(
            template=template, dag_id="hello_world", schedule="* * * * *"
        )

        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "dags"),
            json=dags,
            status=200,
        )
        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "dags/same_old/dagRuns?order_by=-end_date"),
            json=dag_runs_same_old,
            status=200,
        )
        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "dags/hello_world/dagRuns?order_by=-end_date"),
            json=dag_runs_hello_world,
            status=200,
        )
        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "variables"),
            json={
                "variables": [
                    {
                        "key": "TEMPLATE_TEST_DAGS",
                        "value": [
                            {
                                "dag_id": "hello_world",
                                "credentials": [],
                                "static_config": {},
                                "report_email": None,
                                "schedule": "* * * * *",
                            }
                        ],
                    }
                ]
            },
            status=200,
        )

        self.client.force_login(self.USER_TAYLOR)
        response = self.client.post(
            reverse(
                "pipelines:environment_sync",
                kwargs={
                    "environment_id": cluster.id,
                    "environment_contenttype_id": ContentType.objects.get_for_model(
                        Cluster
                    ).id,
                },
            ),
        )
        self.assertRedirects(
            response,
            reverse(
                "connector_airflow:cluster_detail", kwargs={"cluster_id": cluster.id}
            ),
            status_code=302,
        )

    @responses.activate
    def test_sync_302_even_if_airflow_fails(self):
        cluster = Cluster.objects.create(
            name="Bad Test cluster", url="https://bad-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        DAG.objects.create(template=template, dag_id="same_old")

        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "dags"),
            json={},
            status=500,
        )

        self.client.force_login(self.USER_TAYLOR)
        with self.assertLogs("hexa", level="ERROR") as cm:
            response = self.client.post(
                reverse(
                    "pipelines:environment_sync",
                    kwargs={
                        "environment_id": cluster.id,
                        "environment_contenttype_id": ContentType.objects.get_for_model(
                            Cluster
                        ).id,
                    },
                ),
                follow=True,
            )
            self.assertRedirects(
                response,
                reverse(
                    "connector_airflow:cluster_detail",
                    kwargs={"cluster_id": cluster.id},
                ),
                status_code=302,
            )
            self.assertEqual(response.status_code, 200)
            message = list(response.context["messages"])[0]
            self.assertEqual(ERROR, message.level)
            self.assertEqual("The environment could not be synced", message.message)
        self.assertIn("Sync failed for environment", cm.output[0])

    @responses.activate
    def test_dag_run_create_200(self):
        cluster = Cluster.objects.create(
            name="Yet another cluster", url="https://yet-another-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        dag = DAG.objects.create(template=template, dag_id="hello_world")
        self.client.force_login(self.USER_TAYLOR)

        response = self.client.get(
            reverse(
                "connector_airflow:dag_run_create",
                kwargs={"dag_id": dag.id},
            ),
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(json.dumps({}), response.context["run_config"])
        self.assertEqual(json.dumps({}), response.context["sample_config"])

    @responses.activate
    def test_dag_run_create_cloned_config_200(self):
        cluster = Cluster.objects.create(
            name="Yet another cluster", url="https://yet-another-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        dag = DAG.objects.create(template=template, dag_id="hello_world")
        cloned_dag_run = DAGRun.objects.create(
            dag=dag,
            conf={"foo": "bar"},
            execution_date=timezone.now().isoformat(),
            state=DAGRunState.SUCCESS,
            run_id="foo_run_1",
        )
        self.client.force_login(self.USER_TAYLOR)

        response = self.client.get(
            reverse(
                "connector_airflow:dag_run_create",
                kwargs={"dag_id": dag.id},
            )
            + f"?conf_from={cloned_dag_run.id}",
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            json.dumps({"foo": "bar"}, indent=2), response.context["run_config"]
        )

    @responses.activate
    def test_dag_run_create_200_with_sample_config(self):
        cluster = Cluster.objects.create(
            name="Yet another cluster", url="https://yet-another-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        dag = DAG.objects.create(
            template=template, dag_id="hello_world", sample_config={"foo": "bar"}
        )
        self.client.force_login(self.USER_TAYLOR)

        response = self.client.get(
            reverse(
                "connector_airflow:dag_run_create",
                kwargs={"dag_id": dag.id},
            ),
        )
        self.assertEqual(
            200,
            response.status_code,
        )
        self.assertEqual(
            json.dumps({"foo": "bar"}, indent=2), response.context["run_config"]
        )
        self.assertEqual(
            json.dumps({"foo": "bar"}, indent=2), response.context["sample_config"]
        )

    @responses.activate
    def test_dag_run_create_post_302(self):
        cluster = Cluster.objects.create(
            name="Yet another cluster", url="https://yet-another-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        responses.add(
            responses.POST,
            urljoin(cluster.api_url, "dags/hello_world/dagRuns"),
            json=dag_run_hello_world_1,
            status=200,
        )

        dag = DAG.objects.create(template=template, dag_id="hello_world")
        self.client.force_login(self.USER_TAYLOR)

        response = self.client.post(
            reverse(
                "connector_airflow:dag_run_create",
                kwargs={"dag_id": dag.id},
            ),
            data={
                "dag_config": '{"value": 2}',
            },
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, len(responses.calls))
        self.assertEqual(1, DAGRun.objects.count())

    @responses.activate
    def test_dag_run_create_post_no_config_302(self):
        cluster = Cluster.objects.create(
            name="Super simple cluster", url="https://super-simple-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        responses.add(
            responses.POST,
            urljoin(cluster.api_url, "dags/hello_world/dagRuns"),
            json=dag_run_hello_world_1,
            status=200,
        )
        dag = DAG.objects.create(template=template, dag_id="hello_world")

        self.client.force_login(self.USER_TAYLOR)
        response = self.client.post(
            reverse(
                "connector_airflow:dag_run_create",
                kwargs={"dag_id": dag.id},
            ),
        )

        self.assertEqual(302, response.status_code)
        self.assertEqual(1, len(responses.calls))
        self.assertEqual(1, DAGRun.objects.count())

    @responses.activate
    def test_dag_run_create_post_invalid_config_200(self):
        cluster = Cluster.objects.create(
            name="Unhappy cluster", url="https://unhappy-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        responses.add(
            responses.POST,
            urljoin(cluster.api_url, "dags/hello_world/dagRuns"),
            json=dag_run_hello_world_1,
            status=200,
        )

        dag = DAG.objects.create(
            template=template, dag_id="hello_world", sample_config={"bar": "baz"}
        )
        self.client.force_login(self.USER_TAYLOR)

        response = self.client.post(
            reverse(
                "connector_airflow:dag_run_create",
                kwargs={"dag_id": dag.id},
            ),
            data={
                "dag_config": '{"damn": "trailing-commas",}',
            },
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(responses.calls))
        self.assertEqual(0, DAGRun.objects.count())
        self.assertEqual('{"damn": "trailing-commas",}', response.context["run_config"])
        self.assertEqual(
            json.dumps({"bar": "baz"}, indent=2), response.context["sample_config"]
        )
