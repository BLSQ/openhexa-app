import os
import re
from contextlib import contextmanager

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


@contextmanager
def get_cursor(db_name: str, cursor=None):
    """
    Context manager that yields a cursor.
    If cursor is provided, yields it directly.
    Otherwise, creates a new connection and cursor.
    """
    if cursor:
        yield cursor
    else:
        conn = None
        try:
            conn = get_database_connection(db_name)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cur:
                yield cur
        finally:
            if conn:
                conn.close()


def validate_db_name(name: str):
    if not name:
        raise ValidationError("Empty value for name")

    if (re.match(r"^[_a-z][a-z0-9_]{,63}$", name)) is None:
        raise ValidationError(
            "Name must contain only lowercase alphanumeric characters, start with a letter or a underscore and with a maximum length of 31 characters"
        )


def create_read_and_write_role(db_name: str, pwd: str, cursor=None):
    """
    Create a read-write role for a database.

    Args:
        db_name: Database name (also the main role name)
        pwd: Password for the read-write role
        cursor: Optional cursor to use (if None, creates its own connection)
    """
    with get_cursor(db_name, cursor) as cur:
        cur.execute(
            sql.SQL("CREATE ROLE {role_name} LOGIN PASSWORD {password};").format(
                role_name=sql.Identifier(db_name), password=sql.Literal(pwd)
            )
        )
        cur.execute(
            sql.SQL("GRANT {role_name} TO {workspace_database_role};").format(
                role_name=sql.Identifier(db_name),
                workspace_database_role=sql.Identifier(
                    settings.WORKSPACES_DATABASE_ROLE
                ),
            )
        )
        cur.execute(
            sql.SQL("GRANT CREATE, CONNECT ON DATABASE {db_name} TO {role};").format(
                db_name=sql.Identifier(db_name),
                role=sql.Identifier(db_name),
            )
        )
        # Starting from PostgreSQL 15+, we need to grant all access to the public schema
        # to the role when creating a database
        # No changes are needed for existing databases, the default behavior is kept
        # More info on https://www.postgresql.org/docs/release/15.0/
        cur.execute(
            sql.SQL("GRANT ALL ON SCHEMA public TO {role}").format(
                role=sql.Identifier(db_name)
            )
        )


def create_read_only_role(db_name: str, ro_pwd: str, cursor=None):
    """
    Create a read-only role for a database.

    Args:
        db_name: Database name (also the main role name)
        ro_pwd: Password for the read-only role
        cursor: Optional cursor to use (if None, creates its own connection)
    """
    ro_role = f"{db_name}_ro"
    with get_cursor(db_name, cursor) as cur:
        cur.execute(
            sql.SQL("CREATE ROLE {role_name} LOGIN PASSWORD {password};").format(
                role_name=sql.Identifier(ro_role), password=sql.Literal(ro_pwd)
            )
        )
        cur.execute(
            sql.SQL("GRANT CONNECT ON DATABASE {db_name} TO {role};").format(
                db_name=sql.Identifier(db_name),
                role=sql.Identifier(ro_role),
            )
        )
        cur.execute(
            sql.SQL("GRANT USAGE ON SCHEMA public TO {role}").format(
                role=sql.Identifier(ro_role)
            )
        )
        cur.execute(
            sql.SQL("GRANT SELECT ON ALL TABLES IN SCHEMA public TO {role}").format(
                role=sql.Identifier(ro_role)
            )
        )
        cur.execute(
            sql.SQL(
                "ALTER DEFAULT PRIVILEGES FOR ROLE {owner_role} IN SCHEMA public "
                "GRANT SELECT ON TABLES TO {ro_role}"
            ).format(
                owner_role=sql.Identifier(db_name),
                ro_role=sql.Identifier(ro_role),
            )
        )


def create_database(db_name: str, pwd: str, ro_pwd: str):
    """
    Create a database and roles associated to it.

    Args:
        db_name: Database name (also used for the main role name)
        pwd: Password for the main read-write role
        ro_pwd: Password for the read-only role
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
            # Set limitations to make sure one workspace doesn't starve the DB server:
            # - Amount of open connections
            # - idle_in_transaction_session_timeout:
            #       Ensure that idle sessions do not hold locks for an unreasonable
            #       amount of time. Set to a low value because idle sessions in transaction
            #       can cause big performance issues.
            # - statement_timeout:
            #       Avoid accumulation of idle sessions over time. Incorrectly terminated
            #       processes could cause idle connections that accumulate over time,
            #       eventually hitting the connection limit.
            #       We've observed this with e.g. PowerBI dashboard refreshes that don't
            #       properly close connections.
            cursor.execute(
                sql.SQL("ALTER DATABASE {db_name} CONNECTION LIMIT 50;").format(
                    db_name=sql.Identifier(db_name),
                )
            )
            cursor.execute(
                sql.SQL(
                    "ALTER DATABASE {db_name} SET idle_in_transaction_session_timeout = '5min';"
                ).format(
                    db_name=sql.Identifier(db_name),
                )
            )
            cursor.execute(
                sql.SQL(
                    "ALTER DATABASE {db_name} SET statement_timeout = '90min';"
                ).format(
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
            create_read_and_write_role(db_name, pwd, cursor)
            create_read_only_role(db_name, ro_pwd, cursor)
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
    Delete database, role, read-only role and all objects associated with them.
    """
    conn = None
    ro_role = f"{db_name}_ro"
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
            cursor.execute(
                sql.SQL("DROP ROLE {role};").format(role=sql.Identifier(ro_role))
            )
    finally:
        if conn:
            conn.close()
