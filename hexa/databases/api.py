import psycopg2
from django.conf import settings
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from hexa.plugins.connector_postgresql.models import Database


def get_db_server_credentials():
    return {
        "role": settings.WORKSPACE_DATABASE_ROLE,
        "password": settings.WORKSPACE_DATABASE_PASSWORD,
        "host": settings.WORKSPACE_DATABASE_HOST,
        "port": settings.WORKSPACE_DATABASE_PORT,
    }


def create_database(db_name: str):
    credentials = get_db_server_credentials()

    role = credentials["role"]
    password = credentials["password"]
    host = credentials["host"]
    port = credentials["port"]

    url = f"postgresql://{role}:{password}@{host}:{port}"
    try:
        conn = psycopg2.connect(url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            # this is not an SQL injection
            cursor.execute('CREATE DATABASE "' + db_name + '";')
            cursor.execute('CREATE ROLE "' + db_name + '";')
            cursor.execute(
                sql.SQL(
                    "GRANT CREATE, CONNECT ON DATABASE {db_name} TO {role};"
                ).format(
                    db_name=sql.Identifier(db_name),
                    role=sql.Identifier(db_name),
                )
            )
        Database.objects.create(
            hostname=host,
            username=role,
            password=password,
            port=port,
            database=db_name,
        )
    finally:
        if conn:
            conn.close()
