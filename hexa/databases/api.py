import psycopg2
from django.conf import settings
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_db_server_credentials():
    return {
        "role": settings.WORKSPACE_DATABASE_ROLE,
        "password": settings.WORKSPACE_DATABASE_PASSWORD,
        "host": settings.WORKSPACE_DATABASE_HOST,
        "port": settings.WORKSPACE_DATABASE_PORT,
    }


def check_db_name(name):
    if not name:
        raise ValueError("rmpty value for database name")

    if len(name) > 31:
        raise ValueError(
            "bad format for database name (name length must be inferior to 31)"
        )

    for c in name.lower():
        if c not in "abcdefghijklmnopqrstuvwxyz0123456789-_":
            raise ValueError("bad format for database name")


def create_database(db_name):
    """
    Create a database and role associated to it
    Args :
    name - database name (it will be used also for the role name)
    pwd  - password used by the created role to connect to the db
    """
    credentials = get_db_server_credentials()

    role = credentials["role"]
    password = credentials["password"]
    host = credentials["host"]
    port = credentials["port"]

    url = f"postgresql://{role}:{password}@{host}:{port}"
    check_db_name(name=db_name)

    try:
        conn = psycopg2.connect(url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("CREATE DATABASE {db_name};").format(
                    db_name=sql.Identifier(db_name),
                )
            )
            cursor.execute(
                sql.SQL("CREATE ROLE {role_name} LOGIN;").format(
                    role_name=sql.Identifier(db_name)
                )
            )
            cursor.execute(
                sql.SQL(
                    "GRANT CREATE, CONNECT ON DATABASE {db_name} TO {role};"
                ).format(
                    db_name=sql.Identifier(db_name),
                    role=sql.Identifier(db_name),
                )
            )
    finally:
        if conn:
            conn.close()
