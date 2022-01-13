from urllib.parse import urljoin

import responses
from django import test
from django.core.exceptions import ObjectDoesNotExist

from hexa.pipelines.models import Index
from hexa.plugins.connector_airflow.models import (
    DAG,
    Cluster,
    DAGPermission,
    DAGRun,
    DAGRunState,
    DAGTemplate,
)
from hexa.plugins.connector_airflow.tests.responses import dag_run_same_old_2
from hexa.plugins.connector_dhis2.models import Credentials, Instance
from hexa.plugins.connector_postgresql.models import Database
from hexa.user_management.models import Membership, Team, User


class DagTemplateTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.CLUSTER = Cluster.objects.create(name="test_cluster", url="https://wap")
        cls.USER_REGULAR = User.objects.create_user(
            "jim@bluesquarehub.com",
            "regular",
        )

        cls.DHIS2_RDC = Instance.objects.create(
            api_credentials=Credentials.objects.create(
                api_url="https://play.invalid/",
                username="admin_rdc",
                password="password",
            ),
            url="https://play.invalid/",
            name="play rdc",
        )
        cls.DHIS2_CMR = Instance.objects.create(
            api_credentials=Credentials.objects.create(
                api_url="https://play.invalid/",
                username="admin_cmr",
                password="password",
            ),
            url="https://play.invalid/",
            name="play cmr",
        )

        cls.DB_RDC = Database.objects.create(
            hostname="127.0.0.1",
            username="rdc-user",
            password="password",
            port=5432,
            database="rdc-db",
        )
        cls.DB_CMR = Database.objects.create(
            hostname="127.0.0.1",
            username="cmr-user",
            password="password",
            port=5432,
            database="cmr-db",
        )

        cls.TEMPLATE_CHIRPS = DAGTemplate.objects.create(
            cluster=cls.CLUSTER, builder="CHIRPS"
        )
        cls.TEMPLATE_PM = DAGTemplate.objects.create(
            cluster=cls.CLUSTER, builder="PAPERMILL"
        )
        cls.TEMPLATE_DHIS2 = DAGTemplate.objects.create(
            cluster=cls.CLUSTER, builder="DHIS2"
        )

        cls.DHIS2_EXTRACT_RDC = DAG.objects.create(
            template=cls.TEMPLATE_DHIS2,
            dag_id="dhis2_extract_rdc",
            description="dhis2 extract rdc",
            sample_config={"start_date": "2021-01-01", "end_date": "2022-01-01"},
            credentials=[
                {
                    "app": "connector_dhis2",
                    "model": "instance",
                    "id": str(cls.DHIS2_RDC.id),
                }
            ],
        )
        cls.DHIS2_EXTRACT_CMR = DAG.objects.create(
            template=cls.TEMPLATE_DHIS2,
            dag_id="dhis2_extract_cmr",
            description="dhis2 extract cmr",
            sample_config={"start_date": "2021-01-01", "end_date": "2022-01-01"},
            credentials=[
                {
                    "app": "connector_dhis2",
                    "model": "instance",
                    "id": str(cls.DHIS2_CMR.id),
                }
            ],
        )

        cls.CHIRPS_EXTRACT_RDC = DAG.objects.create(
            template=cls.TEMPLATE_CHIRPS,
            dag_id="chirps_extract_rdc",
            description="chirps extract rdc",
            sample_config={"start_date": "2000-01-01"},
            config={
                "download_output_dir": "s3://invalid@/africa/chirps/rainfall/",
                "code": "RDC",
                "contours": "s3://invalid@/geodata/rdc.gpkg",
                "output_dir": "s3://invalid@/data/rainfall",
                "weekly_table": "weekly_auto",
                "monthly_table": "monthly_auto",
            },
            credentials=[
                {
                    "app": "connector_postgresql",
                    "model": "database",
                    "id": str(cls.DB_RDC.id),
                }
            ],
            user=cls.USER_REGULAR,
            schedule="0 12 * * 0",
        )
        cls.CHIRPS_EXTRACT_CMR = DAG.objects.create(
            template=cls.TEMPLATE_CHIRPS,
            dag_id="chirps_extract_cmr",
            description="chirps extract cmr",
            sample_config={"start_date": "2000-01-01"},
            config={
                "download_output_dir": "s3://invalid@/africa/chirps/rainfall/",
                "code": "CMR",
                "contours": "s3://invalid@/geodata/cmr.gpkg",
                "output_dir": "s3://invalid@/data/rainfall",
                "weekly_table": "weekly_auto",
                "monthly_table": "monthly_auto",
            },
            credentials=[
                {
                    "app": "connector_postgresql",
                    "model": "database",
                    "id": str(cls.DB_CMR.id),
                }
            ],
            user=cls.USER_REGULAR,
            schedule="0 12 * * 0",
        )

        cls.PM_GENERIC = DAG.objects.create(
            template=cls.TEMPLATE_PM,
            dag_id="papermill_manual",
            description="Generic Papermill pipeline",
            sample_config={
                "in_notebook": "",
                "out_notebook": "",
                "parameters": {"alpha": 10},
            },
        )
        cls.PM_IHP = DAG.objects.create(
            template=cls.TEMPLATE_PM,
            dag_id="ihp_update",
            description="ihp update dashboard",
            sample_config={
                "in_notebook": "s3://invalid-bucket/code/launch_ihp.ipynb",
                "out_notebook": "s3://invalid-bucket/code/output/ihp_manual_2021-01-01.ipynb",
                "parameters": {"quarter": "2010-Q1"},
            },
            config={
                "in_notebook": "s3://invalid-bucket/code/launch_ihp.ipynb",
                "out_notebook": "s3://invalid-bucket/code/output/ihp_{{ execution_date }}.ipynb",
                "parameters": {},
            },
            credentials=[
                {
                    "app": "connector_dhis2",
                    "model": "instance",
                    "id": str(cls.DHIS2_RDC.id),
                }
            ],
            user=cls.USER_REGULAR,
            schedule="0 12 25 * *",
        )
        cls.PM_IMPERFA = DAG.objects.create(
            template=cls.TEMPLATE_PM,
            dag_id="imperfa_update",
            description="Check RDC quality + update IMPERFA Dashboard",
            sample_config={
                "in_notebook": "s3://invalid-bucket/code/rdc_dqa.ipynb",
                "out_notebook": "s3://invalid-bucket/code/output/rdc_dqa_manual_2021-01-01.ipynb",
                "parameters": {"quarter": "2010-Q1"},
            },
            config={
                "in_notebook": "s3://invalid-bucket/code/rdc_dqa.ipynb",
                "out_notebook": "s3://invalid-bucket/code/output/rdc_dqa_{{ execution_date }}.ipynb",
                "parameters": {},
            },
            user=cls.USER_REGULAR,
            schedule="0 12 20 * *",
        )

    def test_render_pipeline(self):
        self.assertEqual(
            self.TEMPLATE_CHIRPS.render_pipelines(),
            [
                {
                    "dag_id": "chirps_extract_cmr",
                    "credentials": [
                        {
                            "hostname": "127.0.0.1",
                            "username": "cmr-user",
                            "password": "password",
                            "port": 5432,
                            "database": "cmr-db",
                        }
                    ],
                    "static_config": {
                        "code": "CMR",
                        "contours": "s3://invalid@/geodata/cmr.gpkg",
                        "output_dir": "s3://invalid@/data/rainfall",
                        "weekly_table": "weekly_auto",
                        "monthly_table": "monthly_auto",
                        "download_output_dir": "s3://invalid@/africa/chirps/rainfall/",
                    },
                    "report_email": "jim@bluesquarehub.com",
                    "schedule": "0 12 * * 0",
                },
                {
                    "dag_id": "chirps_extract_rdc",
                    "credentials": [
                        {
                            "hostname": "127.0.0.1",
                            "username": "rdc-user",
                            "password": "password",
                            "port": 5432,
                            "database": "rdc-db",
                        }
                    ],
                    "static_config": {
                        "code": "RDC",
                        "contours": "s3://invalid@/geodata/rdc.gpkg",
                        "output_dir": "s3://invalid@/data/rainfall",
                        "weekly_table": "weekly_auto",
                        "monthly_table": "monthly_auto",
                        "download_output_dir": "s3://invalid@/africa/chirps/rainfall/",
                    },
                    "report_email": "jim@bluesquarehub.com",
                    "schedule": "0 12 * * 0",
                },
            ],
        )
        self.assertEqual(
            self.TEMPLATE_DHIS2.render_pipelines(),
            [
                {
                    "dag_id": "dhis2_extract_cmr",
                    "credentials": [
                        {
                            "name": "play cmr",
                            "url": "https://play.invalid/",
                            "username": "admin_cmr",
                            "password": "password",
                        }
                    ],
                    "static_config": {},
                    "report_email": None,
                    "schedule": None,
                },
                {
                    "dag_id": "dhis2_extract_rdc",
                    "credentials": [
                        {
                            "name": "play rdc",
                            "url": "https://play.invalid/",
                            "username": "admin_rdc",
                            "password": "password",
                        }
                    ],
                    "static_config": {},
                    "report_email": None,
                    "schedule": None,
                },
            ],
        )
        self.assertEqual(
            self.TEMPLATE_PM.render_pipelines(),
            [
                {
                    "dag_id": "ihp_update",
                    "credentials": [
                        {
                            "name": "play rdc",
                            "url": "https://play.invalid/",
                            "username": "admin_rdc",
                            "password": "password",
                        }
                    ],
                    "static_config": {
                        "parameters": {},
                        "in_notebook": "s3://invalid-bucket/code/launch_ihp.ipynb",
                        "out_notebook": "s3://invalid-bucket/code/output/ihp_{{ execution_date }}.ipynb",
                    },
                    "report_email": "jim@bluesquarehub.com",
                    "schedule": "0 12 25 * *",
                },
                {
                    "dag_id": "imperfa_update",
                    "credentials": [],
                    "static_config": {
                        "parameters": {},
                        "in_notebook": "s3://invalid-bucket/code/rdc_dqa.ipynb",
                        "out_notebook": "s3://invalid-bucket/code/output/rdc_dqa_{{ execution_date }}.ipynb",
                    },
                    "report_email": "jim@bluesquarehub.com",
                    "schedule": "0 12 20 * *",
                },
                {
                    "dag_id": "papermill_manual",
                    "credentials": [],
                    "static_config": {},
                    "report_email": None,
                    "schedule": None,
                },
            ],
        )


class DAGSyncTest(test.TestCase):
    @responses.activate
    @test.override_settings(AIRFLOW_SYNC_WAIT=0.1)
    def test_sync_airflow(self):
        cluster = Cluster.objects.create(name="cluster", url="https://cluster")
        template = DAGTemplate.objects.create(cluster=cluster, builder="PAPERMILL")
        dag = DAG.objects.create(
            template=template, dag_id="ihp_update", schedule="10 10 * * 1"
        )

        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "dags"),
            json={
                "dags": [
                    {
                        "dag_id": "ihp_update",
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
            responses.GET,
            urljoin(cluster.api_url, "dags/ihp_update/dagRuns?order_by=-end_date"),
            json={
                "dag_runs": [
                    {
                        "conf": {},
                        "dag_id": "ihp_update",
                        "dag_run_id": "ihp_update_id1",
                        "end_date": "2021-10-08T16:43:16.629694+00:00",
                        "execution_date": "2021-10-08T16:42:00+00:00",
                        "external_trigger": False,
                        "start_date": "2021-10-08T16:43:01.101863+00:00",
                        "state": "success",
                    }
                ]
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
                "key": "BUILD_TEST_DAGS",
                "value": """[
  {
    "dag_id": "ihp_update",
    "credentials": [],
    "static_config": {},
    "report_email": None,
    "schedule": "10 10 * * 1"
  }
]""",
            },
            status=200,
        )
        cluster.sync()
        dag.refresh_from_db()
        self.assertEqual(DAGRun.objects.count(), 1)
        self.assertEqual(dag.description, "test dag from factory")


class ModelsTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.CLUSTER = Cluster.objects.create(name="test_cluster")
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

        cluster = Cluster(name="test_cluster")
        cluster.save()

        # Expected index for super users
        pipeline_index = Index.objects.filter_for_user(self.USER_SUPER).get(
            object_id=cluster.id,
        )
        self.assertEqual("test_cluster", pipeline_index.external_name)

        # No permission, no index
        with self.assertRaises(ObjectDoesNotExist):
            Index.objects.filter_for_user(self.USER_REGULAR).get(
                object_id=cluster.id,
            )

    @responses.activate
    def test_dag_run(self):
        cluster = Cluster.objects.create(
            name="test_cluster",
            url="https://airflow-test.openhexa.org",
            username="yolo",
            password="yolo",
        )
        template = DAGTemplate.objects.create(cluster=cluster, builder="TEST")
        dag = DAG.objects.create(template=template, dag_id="same_old")

        responses.add(
            responses.POST,
            urljoin(cluster.api_url, f"dags/{dag.dag_id}/dagRuns"),
            json=dag_run_same_old_2,
            status=200,
        )

        run = dag.run(user=self.USER_REGULAR, conf={"foo": "bar"})

        self.assertIsInstance(run, DAGRun)
        self.assertEqual(self.USER_REGULAR, run.user)
        self.assertEqual({"foo": "bar"}, run.conf)
        self.assertEqual(DAGRunState.QUEUED, run.state)


class PermissionTest(test.TestCase):
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
            template = DAGTemplate.objects.create(cluster=cluster, builder="TEST")
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
