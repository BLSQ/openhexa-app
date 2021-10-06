from django import test
from django.urls import reverse

from hexa.plugins.connector_airflow.datacards import ClusterCard
from hexa.plugins.connector_airflow.models import DAG, Cluster
from hexa.user_management.models import User


class ViewsTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_TAYLOR = User.objects.create_user(
            "taylor@bluesquarehub.com",
            "taylorrocks66",
            is_superuser=True,
        )

    def test_cluster_detail_200(self):
        cluster = Cluster.objects.create(
            name="Test cluster 1 ", url="http://one-cluster-url.com"
        )
        DAG.objects.create(cluster=cluster, dag_id="Test DAG 1 ")
        DAG.objects.create(cluster=cluster, dag_id="Test DAG 2")

        self.client.force_login(self.USER_TAYLOR)
        response = self.client.get(
            reverse(
                "connector_airflow:cluster_detail", kwargs={"cluster_id": cluster.id}
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["cluster_card"], ClusterCard)
        self.assertEqual(2, len(response.context["dag_grid"]))
