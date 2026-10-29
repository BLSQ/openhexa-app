"""Workspace database copier.

Copies the database natively (``CREATE DATABASE ... WITH TEMPLATE``, see
:func:`hexa.databases.api.replace_empty_database_with_copy`) when the run is a
same-server copy. Otherwise the database is skipped with instructions to copy it
separately.
"""

import psycopg2

from hexa.databases.api import (
    DatabaseInUse,
    DatabaseNotEmpty,
    replace_empty_database_with_copy,
)
from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.options import CopyOptions
from hexa.workspace_copier.progress import ProgressReporter
from hexa.workspace_copier.resources.base import ResourceCopier
from hexa.workspace_copier.results import CopyResult, DatabaseResult
from hexa.workspaces.models import Workspace

NOT_ON_THIS_SERVER = (
    "the workspaces are not both on this server: run the copy without the "
    "same-server option."
)


def copy_instructions(source_slug: str, target_slug: str) -> str:
    return "\n".join(
        [
            "If both workspaces are on the same server, copy it natively by running "
            "this on that server:",
            "  ./manage.py copy_workspace --same-server --source-workspace-slug "
            f"{source_slug} --target-workspace-slug {target_slug} --resources "
            "database --source-token <token> --target-token <token>",
            "Otherwise, copy it manually from a machine that has pg_dump / "
            "pg_restore and can reach both database servers:",
            "  1. Set SOURCE_URL and TARGET_URL to the `url` shown on the Database "
            f"page of each workspace (/workspaces/{source_slug}/databases on the "
            f"source server, /workspaces/{target_slug}/databases on the target server).",
            "  2. Run:",
            '     pg_dump -Fc --no-owner --no-acl "$SOURCE_URL" '
            '| pg_restore --no-owner --no-acl -d "$TARGET_URL"',
            "     Errors about the postgis / postgis_topology extensions are "
            "expected and can be ignored.",
        ]
    )


class DatabaseCopier(ResourceCopier):
    name = "database"
    label = "Workspace database"
    help_text = (
        'Only with "Both workspaces are on this server". The source database '
        "must have no open connection, and a target database that already holds "
        "data is left untouched."
    )

    def copy(
        self,
        source: Endpoint,
        target: Endpoint,
        result: CopyResult,
        reporter: ProgressReporter,
        *,
        options: CopyOptions = CopyOptions(),
    ) -> None:
        result.database = DatabaseResult()
        if not options.same_server:
            instructions = copy_instructions(source.slug, target.slug)
            self._skip(
                result,
                reporter,
                "the database is only copied when both workspaces are on this "
                f"server (same-server copy).\n{instructions}",
            )
            return
        source_ws = Workspace.objects.filter(slug=source.slug).first()
        target_ws = Workspace.objects.filter(slug=target.slug).first()
        if source_ws is None or target_ws is None:
            self._fail(result, reporter, NOT_ON_THIS_SERVER)
            return

        reporter.info(
            f"   copying database of '{source_ws.slug}' into '{target_ws.slug}' ..."
        )
        try:
            replace_empty_database_with_copy(source_ws.db_name, target_ws.db_name)
        except DatabaseNotEmpty as exc:
            self._skip(result, reporter, str(exc))
            return
        except DatabaseInUse as exc:
            self._fail(
                result,
                reporter,
                f"{exc}. Close these sessions (notebooks, pipelines, BI tools...) "
                "and re-run into the same target workspace.",
            )
            return
        except psycopg2.Error as exc:
            self._fail(result, reporter, str(exc).strip())
            return

        result.database.copied = True
        reporter.info("   database copied")

    def _skip(self, result: CopyResult, reporter: ProgressReporter, reason: str):
        result.database.skipped = reason
        reporter.warning(f"   database skipped: {reason}")

    def _fail(self, result: CopyResult, reporter: ProgressReporter, reason: str):
        result.database.failed = reason
        reporter.error(f"   database could not be copied: {reason}")
