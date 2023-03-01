import re

import psycopg2
from django.conf import settings
from django.core.exceptions import ValidationError
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_db_server_credentials():
    return {
        "role": settings.WORKSPACES_DATABASE_ROLE,
        "password": settings.WORKSPACES_DATABASE_PASSWORD,
        "host": settings.WORKSPACES_DATABASE_HOST,
        "port": settings.WORKSPACES_DATABASE_PORT,
    }


def get_database_connection(database: str = ""):
    credentials = get_db_server_credentials()
    role = credentials["role"]
    password = credentials["password"]
    host = credentials["host"]
    port = credentials["port"]

    return psycopg2.connect(
        host=host, port=port, dbname=database, user=role, password=password
    )


def format_db_name(name: str):
    db_name = ""
    for char in name.lower().replace("-", "_"):
        if char in "abcdefghijklmnopqrstuvwxyz0123456789_":
            db_name += char

    # Ensure db_name do not start with a number
    if db_name[0] in "0123456789":
        db_name = "_" + db_name

    return db_name[:31]


def validate_db_name(name: str):
    if not name:
        raise ValidationError("Empty value for name")

    if (re.match(r"^[_a-z][a-z0-9_]{,30}$", name)) is None:
        raise ValidationError(
            "Name must contain only lowercase alphanumeric characters, start with a letter or a underscore and with a maximum length of 31 characters"
        )


def create_database(db_name: str, pwd: str):
    """
    Create a database and role associated to it
    Args :
    name - database name (it will be used also for the role name)
    pwd  - password used by the created role to connect to the db
    """

    validate_db_name(db_name)
    conn = None
    try:
        conn = get_database_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("CREATE DATABASE {db_name};").format(
                    db_name=sql.Identifier(db_name),
                )
            )
            cursor.execute(
                sql.SQL("REVOKE ALL ON DATABASE {db_name} FROM PUBLIC;").format(
                    db_name=sql.Identifier(db_name),
                )
            )
            cursor.execute(
                sql.SQL("CREATE ROLE {role_name} LOGIN PASSWORD {password};").format(
                    role_name=sql.Identifier(db_name), password=sql.Literal(pwd)
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

    # load extensions into the new db
    try:
        conn = get_database_connection(db_name)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            cursor.execute("create extension postgis;")
            cursor.execute("create extension postgis_topology;")

    finally:
        if conn:
            conn.close()


def update_database_password(db_role: str, new_password: str):
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
                sql.SQL("ALTER ROLE {role} WITH PASSWORD {password};").format(
                    role=sql.Identifier(db_role), password=sql.Literal(new_password)
                )
            )
    finally:
        if conn:
            conn.close()
