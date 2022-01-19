from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import Project
from hexa.user_management.models import User


class AccessmodGraphTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_1 = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimrocks",
        )
        cls.USER_2 = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janesthebest",
        )
        cls.SAMPLE_PROJECT = Project.objects.create(
            name="Sample project", country="BE", owner=cls.USER_1
        )

    def test_accessmod_project_owner(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessModProject($id: String!) {
                  accessModProject(id: $id) {
                    id
                    name
                    country {
                        code
                    }
                    owner {
                        email
                    }
                  }
                }
            """,
            {"id": str(self.SAMPLE_PROJECT.id)},
        )

        self.assertEqual(
            r["data"]["accessModProject"],
            {
                "id": str(self.SAMPLE_PROJECT.id),
                "name": "Sample project",
                "country": {"code": "BE"},
                "owner": {"email": "jim@bluesquarehub.com"},
            },
        )

    def test_accessmod_project_not_owner(self):
        self.client.force_login(self.USER_2)

        r = self.run_query(
            """
                query accessModProject($id: String!) {
                  accessModProject(id: $id) {
                    id
                  }
                }
            """,
            {"id": str(self.SAMPLE_PROJECT.id)},
        )

        self.assertEqual(
            r["data"]["accessModProject"],
            None,
        )
