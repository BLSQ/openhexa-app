from django import test
from django.urls import reverse

from hexa.plugins.connector_airflow.models import DAG, Cluster, ClusterPermission
from hexa.user_management.models import Membership, Team, User


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
        DAG.objects.create(cluster=cluster_1, dag_id="Test DAG 1 ")
        DAG.objects.create(cluster=cluster_2, dag_id="Test DAG 2")

        self.client.force_login(self.USER_JANE)
        response = self.client.get(
            reverse(
                "pipelines:index",
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, len(response.context["environment_grid"]))
        self.assertEqual(2, len(response.context["pipeline_grid"]))


class IndexPermissionTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
            is_superuser=False,
        )
        cls.CLUSTER = Cluster.objects.create(name="TestCluster", url="http://invalid")
        cls.DAG = DAG.objects.create(cluster=cls.CLUSTER, dag_id="TestDAG")
        cls.TEAM = Team.objects.create(name="JaneTeam")
        Membership.objects.create(team=cls.TEAM, user=cls.USER_JANE)

    def test_loading_perm(self):
        self.client.force_login(self.USER_JANE)

        # regular user + no perm -> empty pipeline index
        response = self.client.get(reverse("pipelines:index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, len(response.context["environment_grid"]))
        self.assertEqual(0, len(response.context["pipeline_grid"]))

        # create team <-> env perm
        ClusterPermission.objects.create(team=self.TEAM, cluster=self.CLUSTER)

        # regular user + perm exists -> pipeline index with 1 cluster and 1 dag
        response = self.client.get(reverse("pipelines:index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, len(response.context["environment_grid"]))
        self.assertEqual(1, len(response.context["pipeline_grid"]))
