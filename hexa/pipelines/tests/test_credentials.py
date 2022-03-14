from hexa.core.test import TestCase
from hexa.plugins.connector_airflow.models import DAG, Cluster, DAGTemplate
from hexa.user_management.models import User


class CredentialsTestCase(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
            is_superuser=True,
        )

        cls.CLUSTER = Cluster.objects.create(
            name="Test cluster 1 ", url="http://one-cluster-url.com"
        )
        cls.TEMPLATE = DAGTemplate.objects.create(cluster=cls.CLUSTER, code="TEST")
        cls.PIPELINE = DAG.objects.create(template=cls.TEMPLATE, dag_id="Test DAG 1")
