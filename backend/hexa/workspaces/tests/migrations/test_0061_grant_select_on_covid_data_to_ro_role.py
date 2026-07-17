from django.test import TransactionTestCase
from psycopg2.errors import (
    InsufficientPrivilege,  # type: ignore[import-not-found] # psycopg2.errors is not in typeshed yet
)

from hexa.core.test.migrator import Migrator
from hexa.databases.api import delete_database
from hexa.databases.tests.helpers import seed_demo_table_as_admin
from hexa.databases.utils import get_workspace_database_ro_connection
from hexa.files import storage
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class Migration0061Test(TransactionTestCase):
    migrate_from = ("workspaces", "0060_grant_create_on_public_to_rw_role")
    migrate_to = ("workspaces", "0061_grant_select_on_covid_data_to_ro_role")

    def setUp(self):
        storage.reset()
        self.migrator = Migrator()
        self.migrator.migrate(*self.migrate_from)

        self.user = User.objects.create_user(
            "migration-test@example.com", "password", is_superuser=True
        )
        self.workspace = Workspace.objects.create_if_has_perm(
            self.user, name="Covid WS", description=""
        )
        seed_demo_table_as_admin(
            self.workspace, [(1, "Kinshasa")], table_name="covid_data"
        )

    def tearDown(self):
        delete_database(self.workspace.db_name)

    def _count_covid_data_as_ro(self):
        conn = get_workspace_database_ro_connection(self.workspace)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM covid_data;")
                return cur.fetchone()[0]
        finally:
            conn.close()

    def test_migration_grants_ro_role_select_on_covid_data(self):
        with self.assertRaises(InsufficientPrivilege):
            self._count_covid_data_as_ro()

        self.migrator.migrate(*self.migrate_to)

        self.assertEqual(self._count_covid_data_as_ro(), 1)
