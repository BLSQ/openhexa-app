from hexa.notebooks.credentials import NotebooksCredentials
from hexa.plugins.connector_postgresql.models import Database


def notebooks_credentials(credentials: NotebooksCredentials):
    """
    Provides the notebooks credentials data that allows users to access SQL Databases
    in the notebooks component.
    """

    databases = Database.objects.filter_for_user(credentials.user)

    if len(databases) > 0:
        pgpass_lines = []

        for database in databases:
            credentials.update_env(
                {
                    f"{database.notebooks_credentials_prefix}_HOSTNAME": database.hostname,
                    f"{database.notebooks_credentials_prefix}_USERNAME": database.username,
                    f"{database.notebooks_credentials_prefix}_PASSWORD": database.password,
                    f"{database.notebooks_credentials_prefix}_DATABASE": database.database,
                    f"{database.notebooks_credentials_prefix}_PORT": str(database.port),
                    f"{database.notebooks_credentials_prefix}_URL": database.url,
                }
            )
            pgpass_lines.append(
                f"{database.hostname}:5432:db_name:{database.username}:{database.password}"
            )

        credentials.update_env(
            {"POSTGRESQL_DATABASE_NAMES": ",".join([x.unique_name for x in databases])}
        )

        if len(pgpass_lines) > 0:
            credentials.files["~/.pgpass"] = "\n".join(pgpass_lines).encode()
        else:
            credentials.files[
                "~/.pgpass"
            ] = b"# This file is empty on purpose as you don't have access to a postgresql database"
