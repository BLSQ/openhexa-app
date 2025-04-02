import psycopg2
from django.core.exceptions import ValidationError
from psycopg2 import OperationalError, sql
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
    def setUpTestData(self):
        super().setUpTestData()
        self.USER_PETE = User.objects.create_user(
            "pete@bluesquarehub.com", "pete's password", is_superuser=True
        )
        self.DB1_NAME = "rdcproject"
        self.PWD_1 = "p%ygy+_'#wd@"
        self.DB2_NAME = "rwandaproject"
        self.PWD_2 = "password_2"

        create_database(self.DB1_NAME, self.PWD_1)
        create_database(self.DB2_NAME, self.PWD_2)

    @classmethod
    def tearDownClass(self):
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
                        db_name=sql.Identifier(self.DB1_NAME),
                    )
                )
                cursor.execute(
                    sql.SQL("DROP DATABASE {db_name};").format(
                        db_name=sql.Identifier(self.DB2_NAME),
                    )
                )
                cursor.execute(
                    sql.SQL("DROP ROLE {role_name};").format(
                        role_name=sql.Identifier(self.DB1_NAME)
                    )
                )
                cursor.execute(
                    sql.SQL("DROP ROLE {role_name};").format(
                        role_name=sql.Identifier(self.DB2_NAME)
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
        with self.assertRaises(ValidationError):
            create_database(bad_input, password)

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

    def test_delete_database(self):
        db_name = "pnlp"
        db_password = "pnlp"
        create_database(db_name, db_password)

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
            conn = psycopg2.connect(url)
