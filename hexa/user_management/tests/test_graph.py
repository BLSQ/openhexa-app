from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User


class UserManagementGraphTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimspassword",
        )

    def test_me_anonymous(self):
        r = self.run_query(
            """
               query {
                  me {
                      id
                  }
                }
            """,
        )

        self.assertEqual(
            None,
            r["data"]["me"],
        )

    def test_me(self):
        self.client.force_login(self.USER)
        r = self.run_query(
            """
               query {
                  me {
                      id
                  }
                }
            """,
        )

        self.assertEqual(
            {"id": str(self.USER.id)},
            r["data"]["me"],
        )

    def test_login(self):
        r = self.run_query(
            """
                mutation login($input: LoginInput!) {
                  login(input: $input) {
                    success
                    me {
                      id
                    }
                  }
                }
            """,
            {"input": {"email": "jim@bluesquarehub.com", "password": "jimspassword"}},
        )

        self.assertEqual(
            {"success": True, "me": {"id": str(self.USER.id)}},
            r["data"]["login"],
        )

    def test_logout(self):
        r = self.run_query(
            """
                mutation {
                  logout {
                    success
                  }
                }
            """,
        )

        self.assertEqual(
            {
                "success": True,
            },
            r["data"]["logout"],
        )

        r = self.run_query(
            """
               query {
                  me {
                      id
                  }
                }
            """,
        )

        self.assertEqual(
            None,
            r["data"]["me"],
        )
