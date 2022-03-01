from hexa.core.test import TestCase
from hexa.plugins.connector_postgresql.models import Database, DatabasePermission, Table
from hexa.user_management.models import Membership, Team, User


class PermissionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.DB1 = Database.objects.create(
            hostname="host", username="user", password="pwd", database="db1"
        )
        cls.DB2 = Database.objects.create(
            hostname="host", username="user", password="pwd", database="db2"
        )
        cls.TEAM1 = Team.objects.create(name="Test Team 1")
        cls.TEAM2 = Team.objects.create(name="Test Team 2")
        DatabasePermission.objects.create(database=cls.DB1, team=cls.TEAM1)
        DatabasePermission.objects.create(database=cls.DB1, team=cls.TEAM2)
        cls.USER_REGULAR = User.objects.create_user(
            "jimmy@bluesquarehub.com",
            "regular",
        )
        Membership.objects.create(team=cls.TEAM1, user=cls.USER_REGULAR)
        Membership.objects.create(team=cls.TEAM2, user=cls.USER_REGULAR)
        cls.USER_SUPER = User.objects.create_user(
            "maryline@bluesquarehub.com",
            "super",
            is_superuser=True,
        )

        for db in [cls.DB1, cls.DB2]:
            for i in range(2):
                Table.objects.create(name=f"table-{db.database}-{i}", database=db)

    def test_instance_dedup(self):
        """
        - user super see 2 db (all of them)
        - user regular see only test db 1, one time
        """
        self.assertEqual(
            list(
                Database.objects.filter_for_user(self.USER_REGULAR)
                .order_by("database")
                .values("database")
            ),
            [{"database": "db1"}],
        )
        self.assertEqual(
            list(
                Database.objects.filter_for_user(self.USER_SUPER)
                .order_by("database")
                .values("database")
            ),
            [{"database": "db1"}, {"database": "db2"}],
        )

    def test_table_dedup(self):
        """
        regular user can see 2 tables
        super user can see 4 tables
        """
        self.assertEqual(
            list(
                Table.objects.filter_for_user(self.USER_REGULAR)
                .order_by("name")
                .values("name")
            ),
            [{"name": "table-db1-0"}, {"name": "table-db1-1"}],
        )
        self.assertEqual(
            list(
                Table.objects.filter_for_user(self.USER_SUPER)
                .order_by("name")
                .values("name")
            ),
            [
                {"name": "table-db1-0"},
                {"name": "table-db1-1"},
                {"name": "table-db2-0"},
                {"name": "table-db2-1"},
            ],
        )
