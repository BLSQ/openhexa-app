import datetime
from unittest import mock
from urllib.parse import urljoin

import responses
from django import test
from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateparse import parse_datetime

from hexa.core.test import TestCase
from hexa.pipelines.models import Index
from hexa.plugins.connector_airflow.models import (
    DAG,
    Cluster,
    DAGAuthorizedDatasource,
    DAGPermission,
    DAGRun,
    DAGRunFavorite,
    DAGRunState,
    DAGTemplate,
)
from hexa.plugins.connector_airflow.tests.responses import dag_run_same_old_2
from hexa.plugins.connector_dhis2.models import Credentials, Instance
from hexa.plugins.connector_postgresql.models import Database
from hexa.user_management.models import Membership, Team, User


class DagTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.CLUSTER = Cluster.objects.create(name="test_cluster", url="https://wap")
        cls.USER_REGULAR = User.objects.create_user(
            "jim@bluesquarehub.com",
            "regular",
        )

        cls.DHIS2_CT1 = Instance.objects.create(
            api_credentials=Credentials.objects.create(
                api_url="https://play.invalid/",
                username="admin_ct1",
                password="password",
            ),
            url="https://play.invalid/",
            name="play ct1",
        )
        cls.DHIS2_CT2 = Instance.objects.create(
            api_credentials=Credentials.objects.create(
                api_url="https://play.invalid/",
                username="admin_ct2",
                password="password",
            ),
            url="https://play.invalid/",
            name="play ct2",
        )

        cls.DB_CT1 = Database.objects.create(
            hostname="127.0.0.1",
            username="ct1-user",
            password="password",
            port=5432,
            database="ct1-db",
        )
        cls.DB_CT2 = Database.objects.create(
            hostname="127.0.0.1",
            username="ct2-user",
            password="password",
            port=5432,
            database="ct2-db",
        )

        cls.TEMPLATE_CHIRPS = DAGTemplate.objects.create(
            cluster=cls.CLUSTER,
            code="CHIRPS",
            description="chirps extract ct1",
            sample_config={"start_date": "2000-01-01"},
        )
        cls.TEMPLATE_PM = DAGTemplate.objects.create(
            cluster=cls.CLUSTER,
            code="PAPERMILL",
            description="Generic Papermill pipeline",
            sample_config={
                "in_notebook": "",
                "out_notebook": "",
                "parameters": {"alpha": 10},
            },
        )
        cls.TEMPLATE_DHIS2 = DAGTemplate.objects.create(
            cluster=cls.CLUSTER,
            code="DHIS2",
            description="dhis2 extract",
            sample_config={"start_date": "2021-01-01", "end_date": "2022-01-01"},
        )

        cls.DHIS2_EXTRACT_CT1 = DAG.objects.create(
            template=cls.TEMPLATE_DHIS2,
            dag_id="dhis2_extract_ct1",
        )
        DAGAuthorizedDatasource.objects.create(
            dag=cls.DHIS2_EXTRACT_CT1, datasource=cls.DHIS2_CT1
        )
        cls.DHIS2_EXTRACT_CT2 = DAG.objects.create(
            template=cls.TEMPLATE_DHIS2,
            dag_id="dhis2_extract_ct2",
        )
        DAGAuthorizedDatasource.objects.create(
            dag=cls.DHIS2_EXTRACT_CT2, datasource=cls.DHIS2_CT2
        )

        cls.CHIRPS_EXTRACT_CT1 = DAG.objects.create(
            template=cls.TEMPLATE_CHIRPS,
            dag_id="chirps_extract_ct1",
            config={
                "download_output_dir": "s3://invalid@/africa/chirps/rainfall/",
                "code": "CT1",
                "contours": "s3://invalid@/geodata/ct1.gpkg",
                "output_dir": "s3://invalid@/data/rainfall",
                "weekly_table": "weekly_auto",
                "monthly_table": "monthly_auto",
            },
            user=cls.USER_REGULAR,
            schedule="0 12 * * 0",
        )
        DAGAuthorizedDatasource.objects.create(
            dag=cls.CHIRPS_EXTRACT_CT1, datasource=cls.DB_CT1
        )
        cls.CHIRPS_EXTRACT_CT2 = DAG.objects.create(
            template=cls.TEMPLATE_CHIRPS,
            dag_id="chirps_extract_ct2",
            config={
                "download_output_dir": "s3://invalid@/africa/chirps/rainfall/",
                "code": "CT2",
                "contours": "s3://invalid@/geodata/ct2.gpkg",
                "output_dir": "s3://invalid@/data/rainfall",
                "weekly_table": "weekly_auto",
                "monthly_table": "monthly_auto",
            },
            user=cls.USER_REGULAR,
            schedule="0 12 * * 0",
        )
        DAGAuthorizedDatasource.objects.create(
            dag=cls.CHIRPS_EXTRACT_CT2, datasource=cls.DB_CT2
        )

        cls.PM_GENERIC = DAG.objects.create(
            template=cls.TEMPLATE_PM,
            dag_id="papermill_manual",
        )
        cls.PM_PRJ1 = DAG.objects.create(
            template=cls.TEMPLATE_PM,
            dag_id="prj1_update",
            config={
                "in_notebook": "s3://invalid-bucket/code/launch_prj1.ipynb",
                "out_notebook": "s3://invalid-bucket/code/output/prj1_{{ execution_date }}.ipynb",
                "parameters": {},
            },
            user=cls.USER_REGULAR,
            schedule="0 12 25 * *",
        )
        DAGAuthorizedDatasource.objects.create(
            dag=cls.PM_PRJ1, datasource=cls.DHIS2_CT1
        )

        cls.PM_PRJ2 = DAG.objects.create(
            template=cls.TEMPLATE_PM,
            dag_id="prj2_update",
            config={
                "in_notebook": "s3://invalid-bucket/code/ct1_dqa.ipynb",
                "out_notebook": "s3://invalid-bucket/code/output/ct1_dqa_{{ execution_date }}.ipynb",
                "parameters": {},
            },
            user=cls.USER_REGULAR,
            schedule="0 12 20 * *",
        )

    def test_build_dag_config(self):
        self.maxDiff = None
        self.assertEqual(
            self.TEMPLATE_CHIRPS.build_dag_config(),
            [
                {
                    "dag_id": "chirps_extract_ct1",
                    "token": self.CHIRPS_EXTRACT_CT1.get_token(),
                    "credentials_url": "http://localhost:8000/pipelines/credentials/",
                    "static_config": {
                        "code": "CT1",
                        "contours": "s3://invalid@/geodata/ct1.gpkg",
                        "output_dir": "s3://invalid@/data/rainfall",
                        "weekly_table": "weekly_auto",
                        "monthly_table": "monthly_auto",
                        "download_output_dir": "s3://invalid@/africa/chirps/rainfall/",
                    },
                    "report_email": "jim@bluesquarehub.com",
                    "schedule": None,  # Was '0 12 * * 0', but we have our own scheduer now
                },
                {
                    "dag_id": "chirps_extract_ct2",
                    "token": self.CHIRPS_EXTRACT_CT2.get_token(),
                    "credentials_url": "http://localhost:8000/pipelines/credentials/",
                    "static_config": {
                        "code": "CT2",
                        "contours": "s3://invalid@/geodata/ct2.gpkg",
                        "output_dir": "s3://invalid@/data/rainfall",
                        "weekly_table": "weekly_auto",
                        "monthly_table": "monthly_auto",
                        "download_output_dir": "s3://invalid@/africa/chirps/rainfall/",
                    },
                    "report_email": "jim@bluesquarehub.com",
                    "schedule": None,  # We '0 12 * * 0', but we have our own scheduer now
                },
            ],
        )
        self.assertEqual(
            self.TEMPLATE_DHIS2.build_dag_config(),
            [
                {
                    "dag_id": "dhis2_extract_ct1",
                    "token": self.DHIS2_EXTRACT_CT1.get_token(),
                    "credentials_url": "http://localhost:8000/pipelines/credentials/",
                    "static_config": {},
                    "report_email": None,
                    "schedule": None,
                },
                {
                    "dag_id": "dhis2_extract_ct2",
                    "token": self.DHIS2_EXTRACT_CT2.get_token(),
                    "credentials_url": "http://localhost:8000/pipelines/credentials/",
                    "static_config": {},
                    "report_email": None,
                    "schedule": None,
                },
            ],
        )
        self.assertEqual(
            self.TEMPLATE_PM.build_dag_config(),
            [
                {
                    "dag_id": "papermill_manual",
                    "token": self.PM_GENERIC.get_token(),
                    "credentials_url": "http://localhost:8000/pipelines/credentials/",
                    "static_config": {},
                    "report_email": None,
                    "schedule": None,
                },
                {
                    "dag_id": "prj1_update",
                    "token": self.PM_PRJ1.get_token(),
                    "credentials_url": "http://localhost:8000/pipelines/credentials/",
                    "static_config": {
                        "parameters": {},
                        "in_notebook": "s3://invalid-bucket/code/launch_prj1.ipynb",
                        "out_notebook": "s3://invalid-bucket/code/output/prj1_{{ execution_date }}.ipynb",
                    },
                    "report_email": "jim@bluesquarehub.com",
                    "schedule": None,  # Was '0 12 25 * *', but we have our own scheduer now
                },
                {
                    "dag_id": "prj2_update",
                    "token": self.PM_PRJ2.get_token(),
                    "credentials_url": "http://localhost:8000/pipelines/credentials/",
                    "static_config": {
                        "parameters": {},
                        "in_notebook": "s3://invalid-bucket/code/ct1_dqa.ipynb",
                        "out_notebook": "s3://invalid-bucket/code/output/ct1_dqa_{{ execution_date }}.ipynb",
                    },
                    "report_email": "jim@bluesquarehub.com",
                    "schedule": None,  # Was '0 12 20 * *' , but we have our own scheduer now
                },
            ],
        )


class DAGSyncTest(TestCase):
    @responses.activate
    @test.override_settings(AIRFLOW_SYNC_WAIT=0.1)
    def test_sync_airflow(self):
        cluster = Cluster.objects.create(name="cluster", url="https://cluster")
        template = DAGTemplate.objects.create(cluster=cluster, code="PAPERMILL")
        dag = DAG.objects.create(
            template=template, dag_id="prj1_update", schedule="10 10 * * 1"
        )

        responses.add(
            responses.GET,
            urljoin(
                cluster.api_url,
                "dags/prj1_update/dagRuns/prj1_update_id1/taskInstances",
            ),
            json={
                "task_instances": [
                    {
                        "state": "success",
                        "task_id": "task-prj1_update",
                    }
                ]
            },
            status=200,
        )
        responses.add(
            responses.GET,
            urljoin(
                cluster.api_url,
                "dags/prj1_update/dagRuns/prj1_update_id1/taskInstances/task-prj1_update/logs/1",
            ),
            body="A nice log is here",
            status=200,
        )

        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "dags"),
            json={
                "dags": [
                    {
                        "dag_id": "prj1_update",
                        "description": "test dag from factory",
                        "file_token": "Ii9vcHQvYWlyZmxvdy9kYWdzL3JlcG8vZGFncy1kZW1vL2hleGFfZmFjdG9yeS5weSI.zP80SU0fjSFxAeXsKHOTAZ3Gs50",
                        "fileloc": "/opt/airflow/dags/repo/dags-demo/hexa_factory.py",
                        "is_active": True,
                        "is_paused": True,
                        "is_subdag": False,
                        "owners": ["airflow"],
                        "root_dag_id": None,
                        "schedule_interval": {
                            "__type": "CronExpression",
                            "value": "10 10 * * 1",
                        },
                        "tags": [],
                    }
                ]
            },
            status=200,
        )
        responses.add(
            responses.PATCH,
            urljoin(cluster.api_url, "dags/prj1_update"),
            json={
                "dags": [
                    {
                        "dag_id": "prj1_update",
                        "description": "test dag from factory",
                        "file_token": "Ii9vcHQvYWlyZmxvdy9kYWdzL3JlcG8vZGFncy1kZW1vL2hleGFfZmFjdG9yeS5weSI.zP80SU0fjSFxAeXsKHOTAZ3Gs50",
                        "fileloc": "/opt/airflow/dags/repo/dags-demo/hexa_factory.py",
                        "is_active": True,
                        "is_paused": False,
                        "is_subdag": False,
                        "owners": ["airflow"],
                        "root_dag_id": None,
                        "schedule_interval": {
                            "__type": "CronExpression",
                            "value": "10 10 * * 1",
                        },
                        "tags": [],
                    }
                ]
            },
            status=200,
        )
        responses.add(
            responses.GET,
            urljoin(
                cluster.api_url,
                "dags/prj1_update/dagRuns?order_by=-end_date&limit=100&offset=0",
            ),
            json={
                "dag_runs": [
                    {
                        "conf": {},
                        "dag_id": "prj1_update",
                        "dag_run_id": "prj1_update_id1",
                        "end_date": "2021-10-08T16:43:16.629694+00:00",
                        "execution_date": "2021-10-08T16:42:00+00:00",
                        "external_trigger": False,
                        "start_date": "2021-10-08T16:43:01.101863+00:00",
                        "state": "success",
                    }
                ],
                "total_entries": 1,
            },
            status=200,
        )
        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "variables"),
            json={"variables": []},
            status=200,
        )
        responses.add(
            responses.POST,
            urljoin(cluster.api_url, "variables"),
            json={
                "key": "TEMPLATE_TEST_DAGS",
                "value": """[
  {
    "dag_id": "prj1_update",
    "env": [],
    "static_config": {},
    "report_email": None,
    "schedule": "10 10 * * 1"
  }
]""",
            },
            status=200,
        )
        responses.add(
            responses.PATCH,
            urljoin(cluster.api_url, "variables/TEMPLATE_TEST_DAGS"),
            json={"variables": []},
            status=200,
        )

        cluster.sync()
        dag.refresh_from_db()
        self.assertEqual(DAGRun.objects.count(), 1)
        self.assertEqual(dag.template.description, "test dag from factory")


class ModelsTest(TestCase):
    @classmethod
    @responses.activate
    def setUpTestData(cls):
        cls.TEAM = Team.objects.create(name="Test Team")
        cls.USER_REGULAR = User.objects.create_user(
            "jim@bluesquarehub.com",
            "regular",
        )
        Membership.objects.create(team=cls.TEAM, user=cls.USER_REGULAR)
        cls.USER_SUPER = User.objects.create_user(
            "mary@bluesquarehub.com",
            "super",
            is_superuser=True,
        )
        cls.CLUSTER = Cluster.objects.create(
            name="test_cluster",
            url="https://airflow-test.openhexa.org",
            username="yolo",
            password="yolo",
        )
        cls.DAG_TEMPLATE = DAGTemplate.objects.create(cluster=cls.CLUSTER, code="TEST")
        cls.DAG = DAG.objects.create(template=cls.DAG_TEMPLATE, dag_id="same_old")
        responses.add(
            responses.POST,
            urljoin(cls.CLUSTER.api_url, f"dags/{cls.DAG.dag_id}/dagRuns"),
            json=dag_run_same_old_2,
            status=200,
        )
        cls.DAG_RUN = cls.DAG.run(
            request=cls.mock_request(cls.USER_REGULAR), conf={"bar": "baz"}
        )

    def test_cluster_without_permission(self):
        """Without creating a permission, a regular user cannot access a cluster"""
        with self.assertRaises(ObjectDoesNotExist):
            Cluster.objects.filter_for_user(self.USER_REGULAR).get(id=self.CLUSTER.id)

    def test_cluster_without_permission_superuser(self):
        """Without creating a permission, a super user can access any cluster"""
        cluster = Cluster.objects.filter_for_user(self.USER_SUPER).get(
            id=self.CLUSTER.id
        )
        self.assertEqual(self.CLUSTER.id, cluster.id)

    def test_cluster_index(self):
        """When a cluster is saved, an index should be created as well (taking access control into account)"""
        self.CLUSTER.save()

        # Expected index for super users
        pipeline_index = Index.objects.filter_for_user(self.USER_SUPER).get(
            object_id=self.CLUSTER.id,
        )
        self.assertEqual("test_cluster", pipeline_index.external_name)

        # No permission, no index
        with self.assertRaises(ObjectDoesNotExist):
            Index.objects.filter_for_user(self.USER_REGULAR).get(
                object_id=self.CLUSTER.id,
            )

    @responses.activate
    def test_dag_run(self):
        responses.add(
            responses.POST,
            urljoin(self.CLUSTER.api_url, f"dags/{self.DAG.dag_id}/dagRuns"),
            json=dag_run_same_old_2,
            status=200,
        )
        run = self.DAG.run(
            request=self.mock_request(self.USER_REGULAR), conf={"foo": "bar"}
        )

        self.assertIsInstance(run, DAGRun)
        self.assertEqual(self.USER_REGULAR, run.user)
        self.assertEqual({"foo": "bar"}, run.conf)
        self.assertEqual(DAGRunState.QUEUED, run.state)

    @responses.activate
    def test_dag_run_duration(self):
        responses.add(
            responses.GET,
            urljoin(
                self.CLUSTER.api_url,
                f"dags/{self.DAG.dag_id}/dagRuns/same_old_run_2/taskInstances",
            ),
            json={
                "task_instances": [
                    {
                        "state": "success",
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
                f"dags/{self.DAG.dag_id}/dagRuns/same_old_run_2/taskInstances/task-prj1_update/logs/1",
            ),
            body="A nice log is here",
            status=200,
        )
        with mock.patch(
            "django.utils.timezone.now",
            return_value=parse_datetime(dag_run_same_old_2["execution_date"])
            + datetime.timedelta(hours=1),
        ):
            end_date = parse_datetime(
                dag_run_same_old_2["execution_date"]
            ) + datetime.timedelta(hours=1)
            self.DAG_RUN.update_state(
                {"state": DAGRunState.SUCCESS, "end_date": end_date.isoformat()}
            )

        self.assertEqual(datetime.timedelta(hours=1), self.DAG_RUN.duration)

    def test_dag_run_toggle_favorite(self):
        favorite = self.DAG_RUN.add_to_favorites(
            user=self.USER_REGULAR, name="My favorite run"
        )
        self.assertIsInstance(favorite, DAGRunFavorite)
        self.assertEqual(self.USER_REGULAR, favorite.user)
        self.assertEqual(self.DAG_RUN, favorite.dag_run)
        self.assertEqual("My favorite run", favorite.name)

        removed = self.DAG_RUN.remove_from_favorites(self.USER_REGULAR)
        self.assertIsNone(removed)
        self.assertFalse(self.DAG_RUN.is_in_favorites(self.USER_REGULAR))

    def test_dag_run_is_in_favorites(self):
        self.assertFalse(self.DAG_RUN.is_in_favorites(self.USER_REGULAR))
        self.DAG_RUN.add_to_favorites(user=self.USER_REGULAR, name="My favorite run")
        self.assertTrue(self.DAG_RUN.is_in_favorites(self.USER_REGULAR))


class PermissionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.CLUSTER1 = Cluster.objects.create(name="test_cluster1")
        cls.CLUSTER2 = Cluster.objects.create(name="test_cluster2")
        cls.TEAM1 = Team.objects.create(name="Test Team1")
        cls.TEAM2 = Team.objects.create(name="Test Team2")
        cls.USER_REGULAR = User.objects.create_user(
            "jim@bluesquarehub.com",
            "regular",
        )
        Membership.objects.create(team=cls.TEAM1, user=cls.USER_REGULAR)
        Membership.objects.create(team=cls.TEAM2, user=cls.USER_REGULAR)
        cls.USER_SUPER = User.objects.create_user(
            "mary@bluesquarehub.com",
            "super",
            is_superuser=True,
        )

        for cluster in [cls.CLUSTER1, cls.CLUSTER2]:
            template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
            for i in range(2):
                dag = DAG.objects.create(
                    dag_id=f"dag-{cluster.name}-{i}", template=template
                )
                if cluster == cls.CLUSTER1:
                    DAGPermission.objects.create(dag=dag, team=cls.TEAM1)
                    DAGPermission.objects.create(dag=dag, team=cls.TEAM2)
                DAGRun.objects.create(
                    dag=dag,
                    run_id=f"dag-run-{cluster.name}-{i}",
                    execution_date="2021-01-01T00:00:00Z",
                    state="success",
                )

    def test_cluster_dedup(self):
        """
        - user super see 2 clusters (all of them)
        - user regular see only test cluster 1, one time
        """
        self.assertEqual(
            list(
                Cluster.objects.filter_for_user(self.USER_REGULAR)
                .order_by("name")
                .values("name")
            ),
            [],
        )
        self.assertEqual(
            list(
                Cluster.objects.filter_for_user(self.USER_SUPER)
                .order_by("name")
                .values("name")
            ),
            [{"name": "test_cluster1"}, {"name": "test_cluster2"}],
        )

    def test_dag_dedup(self):
        """
        regular user can see 2 dags, 2 dag configs, 2 dag runs
        super user can see 4 dags, 4 dag configs, 4 dag runs
        """
        self.assertEqual(
            list(
                DAG.objects.filter_for_user(self.USER_REGULAR)
                .order_by("dag_id")
                .values("dag_id")
            ),
            [{"dag_id": "dag-test_cluster1-0"}, {"dag_id": "dag-test_cluster1-1"}],
        )
        self.assertEqual(
            list(
                DAG.objects.filter_for_user(self.USER_SUPER)
                .order_by("dag_id")
                .values("dag_id")
            ),
            [
                {"dag_id": "dag-test_cluster1-0"},
                {"dag_id": "dag-test_cluster1-1"},
                {"dag_id": "dag-test_cluster2-0"},
                {"dag_id": "dag-test_cluster2-1"},
            ],
        )
        self.assertEqual(
            list(
                DAGRun.objects.filter_for_user(self.USER_REGULAR)
                .order_by("run_id")
                .values("run_id")
            ),
            [
                {"run_id": "dag-run-test_cluster1-0"},
                {"run_id": "dag-run-test_cluster1-1"},
            ],
        )
        self.assertEqual(
            list(
                DAGRun.objects.filter_for_user(self.USER_SUPER)
                .order_by("run_id")
                .values("run_id")
            ),
            [
                {"run_id": "dag-run-test_cluster1-0"},
                {"run_id": "dag-run-test_cluster1-1"},
                {"run_id": "dag-run-test_cluster2-0"},
                {"run_id": "dag-run-test_cluster2-1"},
            ],
        )
