from unittest import mock

from django.utils import timezone

from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_airflow.models import (
    DAG,
    Cluster,
    DAGPermission,
    DAGTemplate,
)
from hexa.plugins.connector_postgresql.models import Database, DatabasePermission
from hexa.plugins.connector_s3.models import Bucket, BucketPermission, Object
from hexa.user_management.models import Membership, Team, User


class CoreDashboardTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):

        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )

        cls.USER_REBECCA = User.objects.create_user(
            "rebecca@bluesquarehub.com",
            "standardpassword",
        )

        cls.TEAM_1 = Team.objects.create(name="Test Team 1")
        cls.TEAM_2 = Team.objects.create(name="Test Team 2")

        Membership.objects.create(user=cls.USER_SABRINA, team=cls.TEAM_1)

        cls.DB = Database.objects.create(
            hostname="host", username="user", password="pwd", database="db1"
        )

        DatabasePermission.objects.create(database=cls.DB, team=cls.TEAM_1)

        # S3 Bucket setup

        cls.BUCKET = Bucket.objects.create(name="test-bucket")
        cls.OBJECT = Object.objects.create(
            bucket=cls.BUCKET, key="file1.ipynb", size=100
        )

        BucketPermission.objects.create(bucket=cls.BUCKET, team=cls.TEAM_1)

        # DAG setup

        cluster = Cluster.objects.create(
            name="Test cluster 2", url="http://another-cluster-url.com"
        )
        template = DAGTemplate.objects.create(cluster=cluster, code="TEST")
        cls.DAG = DAG.objects.create(template=template, dag_id="Test DAG 1 ")

        DAGPermission.objects.create(dag=cls.DAG, team=cls.TEAM_1)

    def test_core_dashboard(self):
        with mock.patch.object(timezone, "now", return_value=timezone.now()):
            self.client.force_login(self.USER_SABRINA)
            r = self.run_query(
                """
                query coreDashboard {
                    coreDashboard {
                    datasources
                    notebooks
                    pipelines
                    lastActivities {
                        description
                        status
                        url
                        occurredAt
                    }
                  }
                }
                """
            )

            self.assertEqual(
                {
                    "datasources": 2,
                    "notebooks": 1,
                    "pipelines": 1,
                    "lastActivities": [
                        {
                            "description": "All datasources are up to date!",
                            "status": "SUCCESS",
                            "url": "/catalog/",
                            "occurredAt": "{}".format(
                                timezone.now()
                                .replace(
                                    hour=0,
                                    minute=0,
                                )
                                .strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
                                + "Z"
                            ),
                        }
                    ],
                },
                r["data"]["coreDashboard"],
            )

    def test_core_dashboard_no_access(self):
        with mock.patch.object(timezone, "now", return_value=timezone.now()):
            self.client.force_login(self.USER_REBECCA)
            r = self.run_query(
                """
                query coreDashboard {
                    coreDashboard {
                    datasources
                    notebooks
                    pipelines
                    lastActivities {
                        description
                        status
                        url
                        occurredAt
                    }
                  }
                }
                """
            )

            self.assertEqual(
                {
                    "datasources": 0,
                    "notebooks": 0,
                    "pipelines": 0,
                    "lastActivities": [
                        {
                            "description": "All datasources are up to date!",
                            "status": "SUCCESS",
                            "url": "/catalog/",
                            "occurredAt": "{}".format(
                                timezone.now()
                                .replace(
                                    hour=0,
                                    minute=0,
                                )
                                .strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
                                + "Z"
                            ),
                        }
                    ],
                },
                r["data"]["coreDashboard"],
            )
