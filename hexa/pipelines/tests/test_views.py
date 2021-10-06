from django import test
from django.urls import reverse
from django.utils import timezone

from hexa.plugins.connector_airflow.models import DAG, Cluster, DAGRun
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
