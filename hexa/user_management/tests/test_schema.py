from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import Membership, MembershipRole, Team, User


class SchemaTest(GraphQLTestCase):
    USER_JIM = None
    USER_JANE = None
    USER_TAYLOR = None
    TEAM_CORE = None
    TEAM_EXTERNAL = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_JIM = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimspassword",
        )
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janespassword",
        )
        cls.USER_TAYLOR = User.objects.create_user(
            "taylor@bluesquarehub.com",
            "taylortaylor2000",
        )
        cls.TEAM_CORE = Team.objects.create(name="Core team")
        Membership.objects.create(
            user=cls.USER_JANE, team=cls.TEAM_CORE, role=MembershipRole.ADMIN
        )
        Membership.objects.create(
            user=cls.USER_JIM, team=cls.TEAM_CORE, role=MembershipRole.REGULAR
        )
        cls.TEAM_EXTERNAL = Team.objects.create(name="External team")
        Membership.objects.create(
            user=cls.USER_TAYLOR, team=cls.TEAM_EXTERNAL, role=MembershipRole.ADMIN
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
        self.client.force_login(self.USER_JIM)
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
            {"id": str(self.USER_JIM.id)},
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
            {"success": True, "me": {"id": str(self.USER_JIM.id)}},
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

    def test_teams_1(self):
        self.client.force_login(self.USER_JIM)

        r = self.run_query(
            """
              query teams {
                teams {
                  pageNumber
                  totalPages
                  totalItems
                  items {
                    id
                    name
                    memberships {
                      pageNumber
                      totalPages
                      totalItems
                      items {
                        user {
                          id
                        }
                        team {
                          id
                        }
                        role
                      }
                    }
                  }
                }
              }
            """,
        )

        self.assertEqual(
            r["data"]["teams"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 1,
                "items": [
                    {
                        "id": str(self.TEAM_CORE.id),
                        "name": self.TEAM_CORE.name,
                        "memberships": {
                            "pageNumber": 1,
                            "totalPages": 1,
                            "totalItems": 2,
                            "items": [
                                {
                                    "user": {"id": str(self.USER_JANE.id)},
                                    "team": {"id": str(self.TEAM_CORE.id)},
                                    "role": MembershipRole.ADMIN,
                                },
                                {
                                    "user": {"id": str(self.USER_JIM.id)},
                                    "team": {"id": str(self.TEAM_CORE.id)},
                                    "role": MembershipRole.REGULAR,
                                },
                            ],
                        },
                    },
                ],
            },
        )

    def test_teams_2(self):
        self.client.force_login(self.USER_TAYLOR)

        r = self.run_query(
            """
              query teams {
                teams {
                  pageNumber
                  totalPages
                  totalItems
                  items {
                    id
                    name
                    memberships {
                      pageNumber
                      totalPages
                      totalItems
                      items {
                        user {
                          id
                        }
                        team {
                          id
                        }
                        role
                      }
                    }
                  }
                }
              }
            """,
        )

        self.assertEqual(
            r["data"]["teams"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 1,
                "items": [
                    {
                        "id": str(self.TEAM_EXTERNAL.id),
                        "name": self.TEAM_EXTERNAL.name,
                        "memberships": {
                            "pageNumber": 1,
                            "totalPages": 1,
                            "totalItems": 1,
                            "items": [
                                {
                                    "user": {"id": str(self.USER_TAYLOR.id)},
                                    "team": {"id": str(self.TEAM_EXTERNAL.id)},
                                    "role": MembershipRole.ADMIN,
                                },
                            ],
                        },
                    },
                ],
            },
        )
