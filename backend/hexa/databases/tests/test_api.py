import psycopg2
from django.core.exceptions import ValidationError
from psycopg2 import OperationalError, sql
from psycopg2.errors import (
    InsufficientPrivilege,  # type: ignore[import-not-found] # psycopg2.errors is not in typeshed yet
)
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, STATUS_READY

from hexa.core.test import TestCase
from hexa.databases.api import (
    create_database,
    delete_database,
    get_database_connection,
    get_db_server_credentials,
    load_database_sample_data,
    update_database_password,
)
from hexa.user_management.models import User


class DatabaseAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.USER_PETE = User.objects.create_user(
            "pete@bluesquarehub.com", "pete's password", is_superuser=True
        )
        cls.DB1_NAME = "rdcproject"
        cls.PWD_1 = "p%ygy+_'#wd@"
        cls.RO_PWD_1 = "ro_p%ygy+_'#wd@"
        cls.DB2_NAME = "rwandaproject"
        cls.PWD_2 = "password_2"
        cls.RO_PWD_2 = "ro_password_2"

        create_database(cls.DB1_NAME, cls.PWD_1, cls.RO_PWD_1)
        create_database(cls.DB2_NAME, cls.PWD_2, cls.RO_PWD_2)

    def _connect_as_main_role(self, autocommit=False):
        """Connect to DB1 using the main read-write role."""
        credentials = get_db_server_credentials()
        conn = psycopg2.connect(
            host=credentials["host"],
            port=credentials["port"],
            dbname=self.DB1_NAME,
            user=self.DB1_NAME,
            password=self.PWD_1,
        )
        if autocommit:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn

    def _connect_as_ro_role(self):
        """Connect to DB1 using the read-only role."""
        credentials = get_db_server_credentials()
        ro_role = f"{self.DB1_NAME}_ro"
        return psycopg2.connect(
            host=credentials["host"],
            port=credentials["port"],
            dbname=self.DB1_NAME,
            user=ro_role,
            password=self.RO_PWD_1,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        credentials = get_db_server_credentials()

        role = credentials["role"]
        password = credentials["password"]
        host = credentials["host"]
        port = credentials["port"]

        url = f"postgresql://{role}:{password}@{host}:{port}"
        conn = None
        try:
            conn = psycopg2.connect(url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute(
                    sql.SQL("DROP DATABASE {db_name};").format(
                        db_name=sql.Identifier(cls.DB1_NAME),
                    )
                )
                cursor.execute(
                    sql.SQL("DROP DATABASE {db_name};").format(
                        db_name=sql.Identifier(cls.DB2_NAME),
                    )
                )
                cursor.execute(
                    sql.SQL("DROP ROLE {role_name};").format(
                        role_name=sql.Identifier(cls.DB1_NAME)
                    )
                )
                cursor.execute(
                    sql.SQL("DROP ROLE {role_name};").format(
                        role_name=sql.Identifier(f"{cls.DB1_NAME}_ro")
                    )
                )
                cursor.execute(
                    sql.SQL("DROP ROLE {role_name};").format(
                        role_name=sql.Identifier(cls.DB2_NAME)
                    )
                )
                cursor.execute(
                    sql.SQL("DROP ROLE {role_name};").format(
                        role_name=sql.Identifier(f"{cls.DB2_NAME}_ro")
                    )
                )

        finally:
            if conn:
                conn.close()

    def test_get_connection_with_special_chars(self):
        with self.settings(
            WORKSPACES_DATABASE_ROLE=self.DB1_NAME,
            WORKSPACES_DATABASE_PASSWORD=self.PWD_1,
        ):
            con = get_database_connection(self.DB1_NAME)
            self.assertEqual(con.status, STATUS_READY)
            con.close()

    def test_create_database_raise_error(self):
        bad_input = "1_invalid_db_name"
        password = "password"
        ro_password = "ro_password"
        with self.assertRaises(ValidationError):
            create_database(bad_input, password, ro_password)

    def test_role_access_denied(self):
        credentials = get_db_server_credentials()

        host = credentials["host"]
        port = credentials["port"]

        # check that role db2 doesn't have access to db1
        url = f"postgresql://{self.DB2_NAME}:{self.PWD_2}@{host}:{port}/{self.DB1_NAME}"

        with self.assertRaises(OperationalError):
            psycopg2.connect(url)

    def test_update_database_password(self):
        new_password = "new_password"

        update_database_password(self.DB2_NAME, new_password)

        credentials = get_db_server_credentials()
        host = credentials["host"]
        port = credentials["port"]

        url = f"postgresql://{self.DB2_NAME}:{self.PWD_2}@{host}:{port}/{self.DB2_NAME}"

        with self.assertRaises(OperationalError):
            psycopg2.connect(url)

    def test_load_database_sample_data(self):
        credentials = get_db_server_credentials()
        host = credentials["host"]
        port = credentials["port"]
        load_database_sample_data(self.DB1_NAME)

        with psycopg2.connect(
            host=host,
            port=port,
            dbname=self.DB1_NAME,
            user=self.DB1_NAME,
            password=self.PWD_1,
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                    SELECT table_name as name, pg_class.reltuples as count
                    FROM information_schema.tables
                    JOIN pg_class ON information_schema.tables.table_name = pg_class.relname
                    WHERE
                        table_schema = 'public' AND
                        table_name NOT IN ('geography_columns', 'geometry_columns', 'spatial_ref_sys')
                    ORDER BY table_name;
                """
            )
            self.assertEqual(len(cursor.fetchall()), 1)

    def test_database_limitation_settings(self):
        """Test that database-level limits are properly configured when creating a database."""
        credentials = get_db_server_credentials()
        host = credentials["host"]
        port = credentials["port"]

        with psycopg2.connect(
            host=host,
            port=port,
            dbname=self.DB1_NAME,
            user=self.DB1_NAME,
            password=self.PWD_1,
        ) as conn:
            cursor = conn.cursor()

            cursor.execute(
                sql.SQL(
                    "SELECT datconnlimit FROM pg_database WHERE datname = {db_name};"
                ).format(db_name=sql.Literal(self.DB1_NAME))
            )
            connection_limit = cursor.fetchone()[0]
            self.assertEqual(connection_limit, 50)

            cursor.execute("SHOW idle_in_transaction_session_timeout;")
            idle_timeout = cursor.fetchone()[0]
            self.assertEqual(idle_timeout, "5min")

            cursor.execute("SHOW statement_timeout;")
            statement_timeout = cursor.fetchone()[0]
            self.assertEqual(statement_timeout, "90min")

    def test_delete_database(self):
        db_name = "pnlp"
        db_password = "pnlp"
        ro_password = "ro_pnlp"
        create_database(db_name, db_password, ro_password)

        credentials = get_db_server_credentials()
        host = credentials["host"]
        port = credentials["port"]

        url = f"postgresql://{db_name}:{db_password}@{host}:{port}/{db_name}"
        conn = None
        try:
            conn = psycopg2.connect(url)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT table_name as name, pg_class.reltuples as count
                FROM information_schema.tables
                JOIN pg_class ON information_schema.tables.table_name = pg_class.relname
                WHERE
                    table_schema = 'public'
                ORDER BY table_name;
             """
            )
            self.assertTrue(len(cursor.fetchall()) > 0)
        finally:
            if conn:
                conn.close()

        delete_database(db_name)
        with self.assertRaises(OperationalError):
            psycopg2.connect(url)

    def test_read_only_role_can_connect(self):
        """Test that the read-only role can connect to the database."""
        with self._connect_as_ro_role() as conn:
            self.assertEqual(conn.status, STATUS_READY)

    def test_read_only_role_can_select(self):
        """Test that the read-only role can SELECT data from tables."""
        with self._connect_as_main_role(autocommit=True) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS test_ro_select (id serial PRIMARY KEY, name text);"
            )
            cursor.execute("INSERT INTO test_ro_select (name) VALUES ('test_data');")

        with self._connect_as_ro_role() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test_ro_select;")
            results = cursor.fetchall()
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0][1], "test_data")

    def test_read_only_role_cannot_insert(self):
        """Test that the read-only role cannot INSERT data."""
        with self._connect_as_main_role(autocommit=True) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS test_ro_insert (id serial PRIMARY KEY, name text);"
            )

        with self._connect_as_ro_role() as conn:
            cursor = conn.cursor()
            with self.assertRaises(InsufficientPrivilege):
                cursor.execute(
                    "INSERT INTO test_ro_insert (name) VALUES ('should_fail');"
                )

    def test_read_only_role_cannot_update(self):
        """Test that the read-only role cannot UPDATE data."""
        with self._connect_as_main_role(autocommit=True) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS test_ro_update (id serial PRIMARY KEY, name text);"
            )
            cursor.execute("INSERT INTO test_ro_update (name) VALUES ('original');")

        with self._connect_as_ro_role() as conn:
            cursor = conn.cursor()
            with self.assertRaises(InsufficientPrivilege):
                cursor.execute(
                    "UPDATE test_ro_update SET name = 'modified' WHERE id = 1;"
                )

    def test_read_only_role_cannot_delete(self):
        """Test that the read-only role cannot DELETE data."""
        with self._connect_as_main_role(autocommit=True) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS test_ro_delete (id serial PRIMARY KEY, name text);"
            )
            cursor.execute("INSERT INTO test_ro_delete (name) VALUES ('to_delete');")

        with self._connect_as_ro_role() as conn:
            cursor = conn.cursor()
            with self.assertRaises(InsufficientPrivilege):
                cursor.execute("DELETE FROM test_ro_delete WHERE id = 1;")

    def test_read_only_role_cannot_create_table(self):
        """Test that the read-only role cannot CREATE tables."""
        with self._connect_as_ro_role() as conn:
            cursor = conn.cursor()
            with self.assertRaises(InsufficientPrivilege):
                cursor.execute("CREATE TABLE should_fail (id serial PRIMARY KEY);")

    def test_read_only_role_cannot_drop_table(self):
        """Test that the read-only role cannot DROP tables."""
        with self._connect_as_main_role(autocommit=True) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS test_ro_drop (id serial PRIMARY KEY);"
            )

        with self._connect_as_ro_role() as conn:
            cursor = conn.cursor()
            with self.assertRaises(InsufficientPrivilege):
                cursor.execute("DROP TABLE test_ro_drop;")

    def test_read_only_role_can_read_new_tables(self):
        """Test that the read-only role can read tables created after the role was set up (default privileges)."""
        with self._connect_as_main_role(autocommit=True) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE new_table_after_ro (id serial PRIMARY KEY, value text);"
            )
            cursor.execute(
                "INSERT INTO new_table_after_ro (value) VALUES ('new_data');"
            )

        with self._connect_as_ro_role() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM new_table_after_ro;")
            results = cursor.fetchall()
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0][1], "new_data")

    def test_read_only_role_cannot_access_other_database(self):
        """Test that the read-only role of one database cannot access another database."""
        credentials = get_db_server_credentials()
        ro_role = f"{self.DB1_NAME}_ro"
        with self.assertRaises(OperationalError):
            psycopg2.connect(
                host=credentials["host"],
                port=credentials["port"],
                dbname=self.DB2_NAME,
                user=ro_role,
                password=self.RO_PWD_1,
            )
