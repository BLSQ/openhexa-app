import re

import psycopg2
from django.conf import settings
from django.core.exceptions import ValidationError
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_db_server_credentials():
    return {
        "role": settings.WORKSPACE_DATABASE_ROLE,
        "password": settings.WORKSPACE_DATABASE_PASSWORD,
        "host": settings.WORKSPACE_DATABASE_HOST,
        "port": settings.WORKSPACE_DATABASE_PORT,
    }


def format_db_name(requestedName: str):
    dbName = ""
    for c in requestedName.lower().replace(" ", "_")[:31]:
        if c in "abcdefghijklmnopqrstuvwxyz0123456789_":
            dbName += c
    return dbName


def validate_db_name(name: str):
    if not name:
        raise ValidationError("Empty value for name")

    if (re.match(r"^[_a-z][a-z0-9_]{,30}$", name)) is None:
        raise ValidationError(
            "Name must contain only lowercase alphanumeric characters, start with a letter or a underscore and with a maximum length of 31 characters"
        )


def create_database(db_name: str):
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
    validate_db_name(db_name)

    try:
        conn = psycopg2.connect(url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("CREATE DATABASE {db_name};").format(
                    db_name=sql.Identifier(db_name),
                )
            )
            cursor.execute("CREATE EXTENSION postgis;")
            cursor.execute("CREATE EXTENSION postgis_topology;")
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
