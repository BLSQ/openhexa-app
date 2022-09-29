import uuid
from datetime import datetime
from unittest import mock
from urllib.parse import urljoin

import responses
from django.core.signing import Signer
from django.urls import reverse
from django.utils import timezone

from hexa.core.test import TestCase
from hexa.plugins.connector_airflow.models import DAG, Cluster, DAGRunState, DAGTemplate
from hexa.user_management.models import User


class WebHookTest(TestCase):
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
        cls.DAG_RUN = cls.DAG.run(
            request=cls.mock_request(cls.USER_TAYLOR),
            webhook_path=reverse("connector_airflow:webhook"),
        )

    def test_webhook_not_authenticated_401(self):
        response = self.client.post(
            reverse(
                "connector_airflow:webhook",
            ),
            {},
        )
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {"success": False},
        )

    def test_webhook_progress_update_200(self):
        response = self.client.post(
            reverse(
                "connector_airflow:webhook",
            ),
            {
                "id": str(uuid.uuid4()),
                "object": "event",
                "created": datetime.timestamp(timezone.now()),
                "type": "progress_update",
                "data": 50,
            },
            **{
                "HTTP_AUTHORIZATION": f"Bearer {Signer().sign_object(self.DAG_RUN.webhook_token)}"
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": True},
        )
        self.DAG_RUN.refresh_from_db()
        self.assertEqual(50, self.DAG_RUN.current_progress)

    def test_webhook_bad_signature(self):
        response = self.client.post(
            reverse(
                "connector_airflow:webhook",
            ),
            {
                "id": str(uuid.uuid4()),
                "object": "event",
                "created": datetime.timestamp(timezone.now()),
                "type": "progress_update",
                "data": 50,
            },
            **{
                "HTTP_AUTHORIZATION": "Bearer 220|zsYv8cs5Kp0v6wlaXYOgI5llzC87kOAV1tjzsmCU"
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {"success": False},
        )

    def test_webhook_log_messages(self):
        utc_now = datetime.utcnow()
        message1 = {
            "priority": "LOG",
            "message": "HelloWorld!",
        }
        message2 = {
            "priority": "ERR",
            "message": "Crashed :/",
        }
        with mock.patch("hexa.plugins.connector_airflow.models.datetime") as mock_date:
            mock_date.utcnow.return_value = utc_now
            mock_date.side_effect = lambda *a, **kw: datetime(*a, **kw)
            response = self.client.post(
                reverse(
                    "connector_airflow:webhook",
                ),
                {
                    "id": str(uuid.uuid4()),
                    "object": "event",
                    "created": datetime.timestamp(timezone.now()),
                    "type": "log_message",
                    "data": message1,
                },
                **{
                    "HTTP_AUTHORIZATION": f"Bearer {Signer().sign_object(self.DAG_RUN.webhook_token)}"
                },
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 200)
            self.assertJSONEqual(
                response.content,
                {"success": True},
            )
            response = self.client.post(
                reverse(
                    "connector_airflow:webhook",
                ),
                {
                    "id": str(uuid.uuid4()),
                    "object": "event",
                    "created": datetime.timestamp(timezone.now()),
                    "type": "log_message",
                    "data": message2,
                },
                **{
                    "HTTP_AUTHORIZATION": f"Bearer {Signer().sign_object(self.DAG_RUN.webhook_token)}"
                },
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": True},
        )

        self.DAG_RUN.refresh_from_db()
        self.assertGreaterEqual(self.DAG_RUN.messages[0].items(), message1.items())
        self.assertGreaterEqual(self.DAG_RUN.messages[1].items(), message2.items())

    @responses.activate
    def test_get_run_logs(self):
        run_logs = "A nice log is here"
        responses.add(
            responses.GET,
            urljoin(
                self.CLUSTER.api_url,
                f"dags/{self.DAG.dag_id}/dagRuns/{self.DAG_RUN.run_id}/taskInstances",
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
                f"dags/{self.DAG.dag_id}/dagRuns/{self.DAG_RUN.run_id}/taskInstances/task-prj1_update/logs/1",
            ),
            body=run_logs,
            status=200,
        )
        run_info = {
            "end_date": "2021-10-09T16:42:16.189200+00:00",
            "state": DAGRunState.SUCCESS,
        }
        self.DAG_RUN.update_state(run_info)
        self.DAG_RUN.refresh_from_db()
        self.assertEqual(100, self.DAG_RUN.current_progress)
        self.assertEqual(f"{run_logs}\n\n\n", self.DAG_RUN.run_logs)
