from django import test
from django.core.exceptions import ObjectDoesNotExist

from hexa.pipelines.models import PipelinesIndexType, PipelinesIndex
from hexa.plugins.connector_airflow.models import Cluster, ClusterPermission
from hexa.user_management.models import Team, User, Membership


class ModelsTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.CLUSTER = Cluster.objects.create(name="test_cluster")
        cls.TEAM = Team.objects.create(name="Test Team")
        cls.USER_REGULAR = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jim@bluesquarehub.com",
            "regular",
        )
        Membership.objects.create(team=cls.TEAM, user=cls.USER_REGULAR)
        cls.USER_SUPER = User.objects.create_user(
            "mary@bluesquarehub.com",
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
        pipeline_index = PipelinesIndex.objects.filter_for_user(self.USER_SUPER).get(
            index_type=PipelinesIndexType.PIPELINES_ENVIRONMENT.value,
            object_id=cluster.id,
        )
        self.assertEqual(
            PipelinesIndexType.PIPELINES_ENVIRONMENT, pipeline_index.index_type
        )
        self.assertEqual("test_cluster", pipeline_index.name)

        # No permission, no index
        with self.assertRaises(ObjectDoesNotExist):
            PipelinesIndex.objects.filter_for_user(self.USER_REGULAR).get(
                index_type=PipelinesIndexType.PIPELINES_ENVIRONMENT.value,
                object_id=cluster.id,
            )

    def test_cluster_index_on_permission_create(self):
        """When creating a cluster permission, the cluster should be re-indexed"""

        ClusterPermission.objects.create(cluster=self.CLUSTER, team=self.TEAM)
        pipeline_index = PipelinesIndex.objects.filter_for_user(self.USER_REGULAR).get(
            index_type=PipelinesIndexType.PIPELINES_ENVIRONMENT.value,
            object_id=self.CLUSTER.id,
        )
        self.assertEqual(
            PipelinesIndexType.PIPELINES_ENVIRONMENT, pipeline_index.index_type
        )
        self.assertEqual("test_cluster", pipeline_index.name)
