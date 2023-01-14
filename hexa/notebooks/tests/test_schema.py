from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User


class NotebooksTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "john@bluesquarehub.com",
            "regular",
        )

    def test_notebooks_url(self):
        self.client.login(email="john@bluesquarehub.com", password="regular")
        with self.settings(NOTEBOOKS_URL="http://localhost:8081"):
            r = self.run_query(
                """
                query notebooksUrl {
                    notebooksUrl
                }

                """
            )
            self.assertEqual(
                "http://localhost:8081",
                r["data"]["notebooksUrl"],
            )
