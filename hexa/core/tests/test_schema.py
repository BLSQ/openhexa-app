from unittest import mock

import pytz
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

        cls.TEAM_1 = Team.objects.create(name="Test Team 1")

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

    def test_core_dashboard_notebooks(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
                query totalNotebooks {
                    totalNotebooks
                }
                """
        )

        self.assertEqual(
            1,
            r["data"]["totalNotebooks"],
        )

    def test_core_dashboard_activities(self):
        with mock.patch.object(
            timezone,
            "now",
            return_value=timezone.datetime(2022, 11, 7, 00, 00, 30, tzinfo=pytz.UTC),
        ):
            self.client.force_login(self.USER_SABRINA)
            r = self.run_query(
                """
                query activities {
                    lastActivities {
                        description
                        status
                        url
                        occurredAt
                    }
                }
                """
            )

            self.assertEqual(
                {
                    "lastActivities": [
                        {
                            "description": "All datasources are up to date!",
                            "status": "SUCCESS",
                            "url": "/catalog/",
                            "occurredAt": "2022-11-07T00:00:30Z",
                        }
                    ],
                },
                r["data"],
            )
