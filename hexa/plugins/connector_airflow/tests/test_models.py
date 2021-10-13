from urllib.parse import urljoin

import responses
from django import test
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from hexa.pipelines.models import Index
from hexa.pipelines.sync import EnvironmentSyncResult
from hexa.plugins.connector_airflow.models import (
    DAG,
    Cluster,
    ClusterPermission,
    DAGRun,
    DAGRunState,
)
from hexa.plugins.connector_airflow.tests.responses import (
    dag_runs_hello_world,
    dag_runs_same_old,
    dags,
)
from hexa.user_management.models import Membership, Team, User


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

        # permission = ClusterPermission.objects.create(cluster=self.CLUSTER, team=self.TEAM)
        with self.assertRaises(ObjectDoesNotExist):
            Cluster.objects.filter_for_user(self.USER_REGULAR).get(id=self.CLUSTER.id)

    def test_cluster_with_permission(self):
        """Given the proper team permission, a regular user can access a cluster"""

        ClusterPermission.objects.create(cluster=self.CLUSTER, team=self.TEAM)
        cluster = Cluster.objects.filter_for_user(self.USER_REGULAR).get(
            id=self.CLUSTER.id
        )
        self.assertEqual(self.CLUSTER.id, cluster.id)

    def test_cluster_without_permission_superuser(self):
        """Without creating a permission, a super user can access any cluster"""

        # permission = ClusterPermission.objects.create(cluster=self.CLUSTER, team=self.TEAM)
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

    def test_cluster_index_on_permission_create(self):
        """When creating a cluster permission, the cluster should be re-indexed"""

        ClusterPermission.objects.create(cluster=self.CLUSTER, team=self.TEAM)
        pipeline_index = Index.objects.filter_for_user(self.USER_REGULAR).get(
            object_id=self.CLUSTER.id,
        )
        self.assertEqual("test_cluster", pipeline_index.external_name)

    @responses.activate
    def test_cluster_sync(self):
        cluster = Cluster.objects.create(
            name="test_cluster",
            url="https://airflow-test.openhexa.org",
            username="yolo",
            password="yolo",
        )
        same_old = DAG.objects.create(cluster=cluster, dag_id="same_old")
        bye_bye = DAG.objects.create(cluster=cluster, dag_id="bye_bye")
        DAGRun.objects.create(
            dag=same_old,
            run_id="same_old_run_1",
            state=DAGRunState.SUCCESS,
            execution_date=timezone.now(),
        )
        DAGRun.objects.create(  # Will be orphaned if all goes well
            dag=same_old,
            run_id="same_old_run_2",
            state=DAGRunState.SUCCESS,
            execution_date=timezone.now(),
        )
        DAGRun.objects.create(
            dag=bye_bye,
            run_id="bye_bye_run_1",
            state=DAGRunState.SUCCESS,
            execution_date=timezone.now(),
        )

        responses.add(
            responses.GET,
            urljoin(cluster.api_url, "dags"),
            json=dags,
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
            urljoin(cluster.api_url, "dags/same_old/dagRuns?order_by=-end_date"),
            json=dag_runs_same_old,
            status=200,
        )

        result = cluster.sync()

        self.assertIsInstance(result, EnvironmentSyncResult)
        self.assertEqual(
            result.orphaned, 2
        )  # The "byebye" DAG should have been orphaned, and one "extra" run for same_old as well
        self.assertEqual(result.created, 3)  # "hello world" DAG + 2 new runs
        self.assertEqual(result.updated, 2)  # "same_old" DAG and its remaining run
        self.assertEqual(2, cluster.dag_set.count())
        self.assertEqual(0, cluster.dag_set.filter(dag_id="bye_bye").count())
        self.assertEqual(3, DAGRun.objects.filter(dag__cluster=cluster).count())
        self.assertEqual(1, DAGRun.objects.filter(dag=same_old).count())
        self.assertEqual(
            0, DAGRun.objects.filter(dag__cluster=cluster, dag=bye_bye).count()
        )
