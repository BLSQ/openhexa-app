from django.db import connection
from django.db.migrations.executor import MigrationExecutor


class Migrator:
    def __init__(self, conn=connection):
        """
        Initialize the Migrator with a database connection.

        :param conn: The database connection to use for migrations.
        """
        self.executor = MigrationExecutor(conn)
        self.apps = None

    def migrate(self, app_label: str, migration: str):
        """
        Apply the specified migration for the given app.

        :param app_label: The label of the app to migrate.
        :param migration: The name of the migration to apply.
        """
        target = [(app_label, migration)]
        self.executor.loader.build_graph()
        self.executor.migrate(target)
        self.apps = self.executor.loader.project_state(target).apps
