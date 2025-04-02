import os
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


def get_database_connection(database: str):
    credentials = get_db_server_credentials()
    role = credentials["role"]
    password = credentials["password"]
    host = credentials["host"]
    port = credentials["port"]

    return psycopg2.connect(
        host=host, port=port, dbname=database, user=role, password=password
    )


def validate_db_name(name: str):
    if not name:
        raise ValidationError("Empty value for name")

    if (re.match(r"^[_a-z][a-z0-9_]{,63}$", name)) is None:
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
        conn = get_database_connection(settings.WORKSPACES_DATABASE_DEFAULT_DB)
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
    finally:
        if conn:
            conn.close()

    #  set role privileges and load extensions
    try:
        conn = get_database_connection(db_name)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
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
            # Starting from PostgreSQL 15+, we need to grand all access to the public schema to the role when creating a database
            # No changes are needed for existing databases, the default behavior is kept
            # More info on https://www.postgresql.org/docs/release/15.0/
            cursor.execute(
                sql.SQL("GRANT ALL ON SCHEMA public TO {role}").format(
                    role=sql.Identifier(db_name)
                )
            )
            cursor.execute("CREATE EXTENSION POSTGIS;")
            cursor.execute("CREATE EXTENSION POSTGIS_TOPOLOGY;")
    finally:
        if conn:
            conn.close()


def update_database_password(db_role: str, new_password: str):
    conn = None
    try:
        conn = get_database_connection(settings.WORKSPACES_DATABASE_DEFAULT_DB)
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


def load_database_sample_data(db_name: str):
    conn = None
    try:
        conn = get_database_connection(db_name)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            with open(
                os.path.join(os.path.dirname(__file__), "static/demo.sql")
            ) as file:
                cursor.execute(file.read())
                cursor.execute(
                    sql.SQL("ALTER TABLE covid_data OWNER TO {role_name};").format(
                        role_name=sql.Identifier(db_name)
                    )
                )

    finally:
        if conn:
            conn.close()


def delete_database(db_name: str):
    """
    Delete database, role and all objects associated with the role.
    """
    conn = None
    try:
        conn = get_database_connection(settings.WORKSPACES_DATABASE_DEFAULT_DB)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("DROP DATABASE {db_name};").format(
                    db_name=sql.Identifier(db_name),
                )
            )
            cursor.execute(
                sql.SQL("DROP OWNED BY {role};").format(role=sql.Identifier(db_name))
            )
            cursor.execute(
                sql.SQL("DROP ROLE {role};").format(role=sql.Identifier(db_name))
            )
    finally:
        if conn:
            conn.close()
