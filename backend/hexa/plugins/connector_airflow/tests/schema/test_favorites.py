from datetime import datetime, timezone

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
        cls.DAG: DAG = DAG.objects.create(
            template=cls.TEMPLATE_DAG,
            dag_id="papermill_manual",
        )
        cls.DAG_PERMISSION = DAGPermission.objects.create(dag=cls.DAG, team=cls.TEAM)

        cls.DAG_RUN: DAGRun = DAGRun.objects.create(
            dag=cls.DAG,
            user=cls.USER_REGULAR,
            conf={"bar": "baz"},
            execution_date=datetime.now(tz=timezone.utc),
        )

    def test_dag_run_not_favorite(self):
        self.client.force_login(self.USER_REGULAR)

        r = self.run_query(
            """
              query run ($id: UUID!) {
                dagRun (id: $id) {
                  id
                  isFavorite
                }
              }
            """,
            {
                "id": str(self.DAG_RUN.id),
            },
        )

        self.assertEqual(
            {"id": str(self.DAG_RUN.id), "isFavorite": False},
            r["data"]["dagRun"],
        )

    def test_dag_run_set_favorite(self):
        self.client.force_login(self.USER_REGULAR)

        r = self.run_query(
            """
            mutation setFavorite ($input: SetDAGRunFavoriteInput!) {
              setDAGRunFavorite(input: $input) {
                success
                errors
                dagRun {
                  id
                  isFavorite
                  label
                }
              }
            }
          """,
            {
                "input": {
                    "id": str(self.DAG_RUN.id),
                    "isFavorite": True,
                    "label": "My favorite run",
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "dagRun": {
                    "id": str(self.DAG_RUN.id),
                    "isFavorite": True,
                    "label": "My favorite run",
                },
            },
            r["data"]["setDAGRunFavorite"],
        )

    def test_dag_run_unset_favorite(self):
        self.client.force_login(self.USER_REGULAR)
        self.DAG_RUN.add_to_favorites(user=self.USER_REGULAR, name="Name")

        self.assertTrue(self.DAG_RUN.is_in_favorites(self.USER_REGULAR))

        r = self.run_query(
            """
            mutation unsetFavorite ($input: SetDAGRunFavoriteInput!) {
              setDAGRunFavorite(input: $input) {
                success
                errors
                dagRun {
                  id
                  isFavorite
                  label
                }
              }
            }
          """,
            {
                "input": {
                    "id": str(self.DAG_RUN.id),
                    "isFavorite": False,
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "dagRun": {
                    "id": str(self.DAG_RUN.id),
                    "isFavorite": False,
                    "label": None,
                },
            },
            r["data"]["setDAGRunFavorite"],
        )
