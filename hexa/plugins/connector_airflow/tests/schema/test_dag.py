from datetime import datetime, timedelta

from django.utils import timezone

from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_airflow.models import (
    DAG,
    Cluster,
    DAGPermission,
    DAGRun,
    DAGTemplate,
)
from hexa.user_management.models import Membership, Team, User


class DAGRunFavoriteTest(GraphQLTestCase):
    USER_REGULAR = None

    @classmethod
    def setUpTestData(cls):
        cls.CLUSTER = Cluster.objects.create(name="test_cluster", url="https://wap")
        cls.USER_REGULAR = User.objects.create_user(
            "jim@bluesquarehub.com",
            "regular",
        )
        cls.TEAM = Team.objects.create(name="Test Team1")
        Membership.objects.create(team=cls.TEAM, user=cls.USER_REGULAR)
        cls.TEMPLATE_DAG = DAGTemplate.objects.create(
            cluster=cls.CLUSTER,
            code="PAPERMILL",
            description="Generic Papermill pipeline",
            sample_config={
                "in_notebook": "",
                "out_notebook": "",
                "parameters": {"alpha": 10},
            },
        )
        cls.DAG_1: DAG = DAG.objects.create(
            template=cls.TEMPLATE_DAG,
            dag_id="papermill_manual",
        )
        cls.DAG_1_PERMISSION = DAGPermission.objects.create(
            dag=cls.DAG_1, team=cls.TEAM
        )

        cls.DAG_1_RUN: DAGRun = DAGRun.objects.create(
            dag=cls.DAG_1,
            user=cls.USER_REGULAR,
            conf={"bar": "baz"},
            execution_date=datetime.now(tz=timezone.utc),
        )
        cls.DAG_2_RUN: DAGRun = DAGRun.objects.create(
            dag=cls.DAG_1,
            user=cls.USER_REGULAR,
            execution_date=datetime.now(tz=timezone.utc) - timedelta(hours=1),
        )

    def test_get_dags(self):
        self.client.force_login(self.USER_REGULAR)
        r = self.run_query(
            """
            query dags {
              dags {
                totalPages
                totalItems
                items {
                  id
                  label
                  formCode
                  externalId
                  description
                  user {
                    id
                  }
                  template {
                    code
                  }
                }
              }
            }
          """,
        )

        self.assertEqual(
            {
                "data": {
                    "dags": {
                        "items": [
                            {
                                "description": "",
                                "externalId": "papermill_manual",
                                "formCode": None,
                                "id": str(self.DAG_1.id),
                                "label": "",
                                "template": {"code": self.TEMPLATE_DAG.code},
                                "user": None,
                            }
                        ],
                        "totalItems": 1,
                        "totalPages": 1,
                    }
                }
            },
            r,
        )

    def test_order_dag_runs(self):
        self.client.force_login(self.USER_REGULAR)
        r = self.run_query(
            """
            query dag($id: String!) {
              dag (id: $id) {
                  id
                  runs {
                      items {
                          id
                      }
                  }
              }
            }
          """,
            {"id": str(self.DAG_1.id)},
        )

        self.assertEqual(
            {
                "data": {
                    "dag": {
                        "id": str(self.DAG_1.id),
                        "runs": {
                            "items": [
                                {"id": str(self.DAG_1_RUN.id)},
                                {"id": str(self.DAG_2_RUN.id)},
                            ]
                        },
                    }
                }
            },
            r,
        )