"""Copy a workspace from one OpenHEXA server to another (CLI wrapper).

Thin wrapper around :func:`hexa.workspace_copier.service.run_copy`.
An omitted/blank ``--source-url`` / ``--target-url`` means the local server.

Auth (per remote side): a ServiceAccount token, sent as an
``Authorization: Bearer`` header on every GraphQL request.
"""

from django.core.management.base import BaseCommand, CommandError

from hexa.workspace_copier.orchestrator import WORKSPACE_COPIERS
from hexa.workspace_copier.progress import StreamReporter
from hexa.workspace_copier.results import format_summary
from hexa.workspace_copier.service import CredentialError, run_copy
from hexa.workspace_copier.transport import GraphQLError


def _known_resource_names() -> set[str]:
    return {c.name for c in WORKSPACE_COPIERS}


class Command(BaseCommand):
    help = "Copy a workspace from one OpenHEXA server to another."

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
        parser.add_argument(
            "--source-token",
            default="",
            help="ServiceAccount token for the source server (remote only).",
        )
        parser.add_argument(
            "--target-url",
            default="",
            help="Target GraphQL endpoint. Blank means the local server.",
        )
        parser.add_argument(
            "--target-token",
            default="",
            help="ServiceAccount token for the target server (remote only).",
        )
        parser.add_argument(
            "--target-organization",
            default=None,
            help="UUID of the organization on the target server. Required unless "
            "--target-workspace-slug is given.",
        )
        parser.add_argument(
            "--target-workspace-name",
            default=None,
            help="Optional name for the target workspace. "
            "Defaults to the source workspace name. "
            "Ignored when --target-workspace-slug is given.",
        )
        parser.add_argument(
            "--target-workspace-slug",
            default=None,
            help="Slug of an existing target workspace to copy into, instead of "
            "creating a new one. Makes the copy idempotent: resources that "
            "already exist are skipped, so an interrupted run can be re-run "
            "safely. Exits early if the slug does not exist on the target.",
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
        target_workspace_slug = options["target_workspace_slug"]

        if not target_workspace_slug and not options["target_organization"]:
            raise CommandError(
                "--target-organization is required unless --target-workspace-slug "
                "is given (re-run into an existing workspace)."
            )
        if target_workspace_slug and options["target_workspace_name"]:
            self.stdout.write(
                "Note: --target-workspace-name is ignored when "
                "--target-workspace-slug is set (the workspace already exists)."
            )

        reporter = StreamReporter(self.stdout)

        try:
            result = run_copy(
                source_url=options["source_url"],
                source_token=options["source_token"],
                source_slug=options["source_workspace_slug"],
                target_url=options["target_url"],
                target_token=options["target_token"],
                target_organization_id=options["target_organization"],
                target_workspace_name=options["target_workspace_name"],
                target_workspace_slug=target_workspace_slug,
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
