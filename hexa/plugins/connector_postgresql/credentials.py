from hexa.notebooks.credentials import NotebooksCredentials
from hexa.plugins.connector_postgresql.models import PostgresqlDatabase


def notebooks_credentials(credentials: NotebooksCredentials):
    """
    Provides the notebooks credentials data that allows users to access SQL Databases
    in the notebooks component.
    """

    databases = PostgresqlDatabase.objects.filter_for_user(credentials.user)

    pgpass_lines = []

    for database in databases:
        credentials.update_env(
            {
                f"{database.env_name}_HOSTNAME": database.hostname,
                f"{database.env_name}_USERNAME": database.username,
                f"{database.env_name}_PASSWORD": database.password,
                f"{database.env_name}_DATABASE": database.database,
                f"{database.env_name}_PORT": str(database.port),
                f"{database.env_name}_URL": database.url,
            }
        )
        pgpass_lines.append(
            f"{database.hostname}:5432:db_name:{database.username}:{database.password}"
        )

    credentials.update_env(
        {f"POSTGRESQL_DATABASE_NAMES": ",".join([x.unique_name for x in databases])}
    )

    if len(pgpass_lines) > 0:
        credentials.files["~/.pgpass"] = "\n".join(pgpass_lines).encode()
    else:
        credentials.files[
            "~/.pgpass"
        ] = "# This file is empty on purpose as you don't have access to a postgresql database".encode()
