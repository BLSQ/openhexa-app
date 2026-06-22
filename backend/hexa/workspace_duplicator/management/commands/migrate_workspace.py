"""Migrate a workspace from one OpenHEXA server to another (CLI wrapper).

Thin wrapper around :func:`hexa.workspace_duplicator.service.run_migration`.
An omitted/blank ``--source-url`` / ``--target-url`` means the local server.

Auth (per remote side): a Django superuser email/password, exchanged for a
session cookie via the GraphQL ``login`` mutation.
"""

from django.core.management.base import BaseCommand, CommandError

from hexa.workspace_duplicator.orchestrator import WORKSPACE_COPIERS
from hexa.workspace_duplicator.progress import StreamReporter
from hexa.workspace_duplicator.results import format_summary
from hexa.workspace_duplicator.service import CredentialError, run_migration
from hexa.workspace_duplicator.transport import GraphQLError


def _known_resource_names() -> set[str]:
    return {c.name for c in WORKSPACE_COPIERS}


class Command(BaseCommand):
    help = "Migrate a workspace from one OpenHEXA server to another."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-workspace-slug",
            required=True,
            help="Slug of the source workspace.",
        )
        parser.add_argument(
            "--source-url",
            default="",
            help="Source GraphQL endpoint. Blank means the local server.",
        )
        parser.add_argument("--source-email", default="")
        parser.add_argument("--source-password", default="")
        parser.add_argument(
            "--target-url",
            default="",
            help="Target GraphQL endpoint. Blank means the local server.",
        )
        parser.add_argument("--target-email", default="")
        parser.add_argument("--target-password", default="")
        parser.add_argument(
            "--target-organization",
            default=None,
            help="Optional UUID of the organization on the target server.",
        )
        parser.add_argument(
            "--target-workspace-name",
            default=None,
            help="Optional name for the target workspace. "
            "Defaults to the source workspace name.",
        )
        parser.add_argument(
            "--resources",
            default=None,
            help="Comma-separated resources to copy (default: all). "
            f"Known: {','.join(sorted(_known_resource_names()))}.",
        )

    def _resolve_resources(self, resources: str | None):
        known = _known_resource_names()
        selected = (
            known.copy()
            if not resources
            else {r.strip() for r in resources.split(",") if r.strip()}
        )

        unknown = selected - known
        if unknown:
            raise CommandError(
                f"unknown resource(s): {', '.join(sorted(unknown))}. "
                f"Known: {', '.join(sorted(known))}."
            )
        return selected

    def handle(self, *args, **options):
        resources = self._resolve_resources(options["resources"])
        reporter = StreamReporter(self.stdout)

        try:
            result = run_migration(
                source_url=options["source_url"],
                source_email=options["source_email"],
                source_password=options["source_password"],
                source_slug=options["source_workspace_slug"],
                target_url=options["target_url"],
                target_email=options["target_email"],
                target_password=options["target_password"],
                target_organization_id=options["target_organization"],
                target_workspace_name=options["target_workspace_name"],
                resources=resources,
                reporter=reporter,
            )
        except CredentialError as exc:
            raise CommandError(
                "Endpoint verification failed:\n"
                + "\n".join(f"  - {e}" for e in exc.errors)
            )
        except GraphQLError as exc:
            raise CommandError(str(exc))

        self.stdout.write(format_summary(result))
