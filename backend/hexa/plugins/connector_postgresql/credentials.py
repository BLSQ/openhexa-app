from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

from django.contrib.contenttypes.models import ContentType

from hexa.notebooks.credentials import NotebooksCredentials
from hexa.pipelines.credentials import PipelinesCredentials
from hexa.plugins.connector_postgresql.models import Database


def get_env(
    databases: List[Tuple[Database, Optional[str]]],
    run_id: Optional[str] = None,
    pipeline_name: Optional[str] = None,
) -> Tuple[Dict[str, str], Dict[str, bytes]]:
    env, files = {}, {}

    if len(databases) > 0:
        pgpass_lines = []

        for database, label in databases:
            if not label:
                label = database.unique_name
            label = label.replace("-", "_").upper()

            db_url = database.url
            if run_id and pipeline_name:
                application_name = f"{pipeline_name} (run {run_id})"
                db_url = f"{db_url}?application_name={quote(application_name)}"

            env[f"POSTGRESQL_{label}_HOSTNAME"] = database.hostname
            env[f"POSTGRESQL_{label}_USERNAME"] = database.username
            env[f"POSTGRESQL_{label}_PASSWORD"] = database.password
            env[f"POSTGRESQL_{label}_DATABASE"] = database.database
            env[f"POSTGRESQL_{label}_PORT"] = str(database.port)
            env[f"POSTGRESQL_{label}_URL"] = db_url

            pgpass_lines.append(
                f"{database.hostname}:5432:db_name:{database.username}:{database.password}"
            )

        env["POSTGRESQL_DATABASE_NAMES"] = ",".join(
            [
                (label if label else database.unique_name).replace("-", "_").upper()
                for database, label in databases
            ]
        )

        if len(pgpass_lines) > 0:
            files["~/.pgpass"] = "\n".join(pgpass_lines).encode()
        else:
            files[
                "~/.pgpass"
            ] = b"# This file is empty on purpose as you don't have access to a postgresql database"

    return env, files


def notebooks_credentials(credentials: NotebooksCredentials):
    """
    Provides the notebooks credentials data that allows users to access SQL Databases
    in the notebooks component.
    """
    databases = Database.objects.filter_for_user(credentials.user)

    env, files = get_env([(x, None) for x in databases])
    credentials.env.update(env)
    credentials.files.update(files)


def pipelines_credentials(credentials: PipelinesCredentials):
    """
    Provides the notebooks credentials data that allows users to access PostgreSQL databases
    in the pipelines component.
    """
    if hasattr(credentials.pipeline, "authorized_datasources"):
        authorized_datasource = credentials.pipeline.authorized_datasources.filter(
            datasource_type=ContentType.objects.get_for_model(Database)
        )
        databases = [(x.datasource, x.slug) for x in authorized_datasource]
    else:
        # Pipelines V2
        authorized_datasource = Database.objects.filter_for_user(
            credentials.pipeline.user
        )
        databases = [(x, None) for x in authorized_datasource]

    # Pass run information for application_name tracking
    env, files = get_env(
        databases, run_id=credentials.run_id, pipeline_name=credentials.pipeline_name
    )

    credentials.env.update(env)
    credentials.files.update(files)
