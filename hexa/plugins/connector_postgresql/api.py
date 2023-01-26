import psycopg2
from django.core.exceptions import ImproperlyConfigured
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from hexa.workspaces.models import WorkspaceDBConfig

from . import models


def create_db(requestedName: str):
    try:
        conf = WorkspaceDBConfig.objects.get()
    except (
        WorkspaceDBConfig.DoesNotExist,
        WorkspaceDBConfig.MultipleObjectsReturned,
    ):
        raise ImproperlyConfigured("The WorkspaceDBConfig is not configured")

    url = f"postgresql://{conf.username}:{conf.password}@{conf.hostname}:{conf.port}"

    # We can't use the mongrify because it will add single quote around
    # the DB name, which is invalid in SQL -> string substitution
    # Since it enables sql injection, be paranoid about the char allowed.
    # Don't use an external dep (like slugify), rules can change based
    # on UTF8 and emoji.. force ascii a-z_-
    # (also, dbname is 31 chars max in postgresql)
    dbName = ""
    for c in requestedName.lower().replace(" ", "-")[:31]:
        if c in "abcdefghijklmnopqrstuvwxyz0123456789-_":
            dbName += c

    try:
        conn = psycopg2.connect(url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            # this is not an SQL injection
            cursor.execute('create database "' + dbName + '";')
        models.Database.objects.create(
            hostname=conf.hostname,
            username=conf.username,
            password=conf.password,
            port=conf.port,
            database=dbName,
        )
    finally:
        if conn:
            conn.close()
