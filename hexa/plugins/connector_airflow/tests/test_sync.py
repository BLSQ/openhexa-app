from urllib.parse import urljoin

import responses
from django import test
from django.utils import timezone

from hexa.plugins.connector_airflow.management.commands.dagruns_continuous_sync import (
    Command,
)
from hexa.plugins.connector_airflow.models import (
    DAG,
    Cluster,
    DAGRun,
    DAGRunState,
    DAGTemplate,
)
from hexa.plugins.connector_airflow.tests.responses import (
    dag_continuous_sync1,
    dag_continuous_sync2,
)
from hexa.user_management.models import User


class ContinuousSyncTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_TAYLOR = User.objects.create_user(
            "taylor@bluesquarehub.com",
            "taylorrocks66",
            is_superuser=True,
        )
        cls.CLUSTER = Cluster.objects.create(
            name="Test cluster", url="https://one-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cls.CLUSTER, code="TEST")
        cls.DAG = DAG.objects.create(template=template, dag_id="hello_world")
        cls.FINISH_RUN = DAGRun.objects.create(
            dag=cls.DAG,
            run_id="run1",
            execution_date=timezone.now(),
            state="success",
        )

    @responses.activate
    def test_continuous_sync_noact(self):
        responses.add(
            responses.GET,
            urljoin(self.CLUSTER.api_url, "dags/~/dagRuns?order_by=-end_date&limit=25"),
            json=dag_continuous_sync1,
            status=200,
        )

        cmd = Command()
        cmd.handle(limit=25, _test_once=True)
        self.assertEqual(DAGRun.objects.all().count(), 1)

    @responses.activate
    def test_continuous_sync_update(self):
        dag_run = DAGRun.objects.create(
            dag=self.DAG,
            run_id="run2",
            execution_date=timezone.now(),
            state=DAGRunState.RUNNING,
        )

        responses.add(
            responses.GET,
            urljoin(self.CLUSTER.api_url, "dags/~/dagRuns?order_by=-end_date&limit=25"),
            json=dag_continuous_sync2,
            status=200,
        )

        cmd = Command()
        cmd.handle(limit=25, _test_once=True)
        self.assertEqual(DAGRun.objects.all().count(), 2)
        dag_run.refresh_from_db()
        self.assertEqual(dag_run.state, DAGRunState.SUCCESS)
