import psycopg2
from django.core.exceptions import ValidationError
from psycopg2 import OperationalError, sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, STATUS_READY

from hexa.core.test import TestCase
from hexa.databases.api import (
    create_database,
    format_db_name,
    get_database_connection,
    get_db_server_credentials,
)
from hexa.user_management.models import User


class DatabaseAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_PETE = User.objects.create_user(
            "pete@bluesquarehub.com", "pete's password", is_superuser=True
        )

    def setUp(self):
        self.DB1_NAME = "rdcproject"
        self.PWD_1 = "p%ygy+_'#wd@"
        create_database(self.DB1_NAME, self.PWD_1)

    def tearDown(self):
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
                    sql.SQL("DROP ROLE {role_name};").format(
                        role_name=sql.Identifier(self.DB1_NAME)
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

    def test_format_db_name(self):
        db_name = "RDC_POLIO_PROJECT"
        self.assertEqual(db_name.lower(), format_db_name(db_name))

        # test with a name with length superior to 31
        db_name = "THIS_IS_A_VERY_LONG_TEXT_WITH_MORE_THAN_31_LETTERS"
        self.assertTrue(len(format_db_name(db_name)) <= 31)

        # test with a name starting with a number
        db_name = "1rwandaProject"
        self.assertEqual("_1rwandaproject", format_db_name(db_name))

    def test_create_database_raise_error(self):
        bad_input = "1_invalid_db_name"
        password = "password"
        with self.assertRaises(ValidationError):
            create_database(bad_input, password)

    def test_create_database_not_access(self):
        password_1 = "password_1"
        password_2 = "password_2"
        create_database(self.DB1_NAME, password_1)
        create_database(self.DB2_NAME, password_2)

        credentials = get_db_server_credentials()

        host = credentials["host"]
        port = credentials["port"]

        # check that role db2 doesn't have access to db1
        url = f"postgresql://{self.DB2_NAME}:{password_2}@{host}:{port}/{self.DB1_NAME}"

        with self.assertRaises(OperationalError):
            conn = psycopg2.connect(url)
