from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User


class SchemaTest(GraphQLTestCase):
    USER_JIM = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_JIM = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimspassword",
        )

    def test_country(self):
        self.client.force_login(self.USER_JIM)
        r = self.run_query(
            """
              query {
                country(code: "BF") {
                  code
                  name
                  alpha3
                  whoInfo {
                    region {
                      code
                      name
                    }
                    defaultCRS
                    simplifiedExtent
                  }
                }
              }
            """,
        )

        self.assertEqual(
            {
                "name": "Burkina Faso",
                "code": "BF",
                "alpha3": "BFA",
                "whoInfo": {
                    "region": {"code": "AFRO", "name": "African Region"},
                    "defaultCRS": 32630,
                    "simplifiedExtent": [],  # FIXME [[x, y] for x, y in SIMPLIFIED_BFA_EXTENT],
                },
            },
            r["data"]["country"],
        )

    def test_countries(self):
        self.client.force_login(self.USER_JIM)
        r = self.run_query(
            """
                  query {
                    countries {
                      code
                      name
                      alpha3
                    }
                  }
                """,
        )

        self.assertEqual(
            {
                "name": "Burkina Faso",
                "code": "BF",
                "alpha3": "BFA",
            },
            next(c for c in r["data"]["countries"] if c["alpha3"] == "BFA"),
        )
