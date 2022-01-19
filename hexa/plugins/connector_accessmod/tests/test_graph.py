from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User


class AccessmodGraphTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "jim@bluesquarehub.com",
            "regular",
            is_superuser=True,
        )

    def test_accessmod_project(self):
        self.client.force_login(self.USER)

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
            {"id": "69fadc86-bfda-40a1-a7b2-de346a790277"},
        )

        self.assertEqual(
            r["data"]["accessModProject"],
            {
                "id": "69fadc86-bfda-40a1-a7b2-de346a790277",
                "name": "Sample project",
                "country": {"code": "BE"},
                "owner": {"email": "jim@bluesquarehub.com"},
            },
        )
