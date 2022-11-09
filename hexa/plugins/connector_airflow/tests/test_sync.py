from unittest.mock import patch
from urllib.parse import urljoin

import responses
from django import test
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.urls import reverse
from django.utils import timezone

from hexa.core.test import TestCase
from hexa.pipelines.queue import environment_sync_queue
from hexa.plugins.connector_airflow.management.commands.dagruns_continuous_sync import (
    Command,
)
from hexa.plugins.connector_airflow.models import (
    DAG,
    Cluster,
    DAGRun,
    DAGRunState,
    DAGTemplate,
    EnvironmentSyncResult,
)
from hexa.plugins.connector_airflow.tests.responses import (
    dag_continuous_sync1,
    dag_continuous_sync2,
)
from hexa.user_management.models import User


class ContinuousSyncTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_TAYLOR = User.objects.create_user(
            "taylor@bluesquarehub.com",
            "taylorrocks66",
            is_superuser=True,
            is_staff=True,
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
            urljoin(
                self.CLUSTER.api_url,
                "dags/~/dagRuns?order_by=-end_date&limit=25&offset=0",
            ),
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
            urljoin(
                self.CLUSTER.api_url,
                f"dags/{self.DAG.dag_id}/dagRuns/run2/taskInstances",
            ),
            json={
                "task_instances": [
                    {
                        "state": "running",
                        "task_id": "task-prj1_update",
                    }
                ]
            },
            status=200,
        )
        responses.add(
            responses.GET,
            urljoin(
                self.CLUSTER.api_url,
                f"dags/{self.DAG.dag_id}/dagRuns/run2/taskInstances/task-prj1_update/logs/1",
            ),
            body="A nice log is here",
            status=200,
        )
        responses.add(
            responses.GET,
            urljoin(
                self.CLUSTER.api_url,
                "dags/~/dagRuns?order_by=-end_date&limit=25&offset=0",
            ),
            json=dag_continuous_sync2,
            status=200,
        )

        cmd = Command()
        cmd.handle(limit=25, _test_once=True)
        self.assertEqual(DAGRun.objects.all().count(), 2)
        dag_run.refresh_from_db()
        self.assertEqual(dag_run.state, DAGRunState.SUCCESS)

    @test.override_settings(EXTERNAL_ASYNC_REFRESH=False)
    def test_adminaction_sync_refresh(self):
        self.client.force_login(self.USER_TAYLOR)
        synced = False

        def mock_sync(self):
            nonlocal synced
            synced = True
            return EnvironmentSyncResult(
                environment=self,
                created=10,
                updated=11,
                identical=12,
                orphaned=13,
            )

        with patch("hexa.plugins.connector_airflow.models.Cluster.sync", mock_sync):
            data = {
                "action": "SyncCluster",
                ACTION_CHECKBOX_NAME: [
                    str(self.CLUSTER.id),
                ],
            }
            url = reverse("admin:connector_airflow_cluster_changelist")
            response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(synced)

    @test.override_settings(EXTERNAL_ASYNC_REFRESH=True)
    def test_adminaction_async_refresh(self):
        self.client.force_login(self.USER_TAYLOR)
        synced = False

        def mock_sync(self):
            nonlocal synced
            synced = True
            return EnvironmentSyncResult(
                environment=self,
                created=10,
                updated=11,
                identical=12,
                orphaned=13,
            )

        with patch("hexa.plugins.connector_airflow.models.Cluster.sync", mock_sync):
            data = {
                "action": "SyncCluster",
                ACTION_CHECKBOX_NAME: [
                    (self.CLUSTER.id),
                ],
            }
            url = reverse("admin:connector_airflow_cluster_changelist")
            response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(synced)

        with patch("hexa.plugins.connector_airflow.models.Cluster.sync", mock_sync):
            while environment_sync_queue.run_once():
                pass

        self.assertTrue(synced)
