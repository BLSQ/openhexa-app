"""Copy all pipeline templates from one OpenHEXA server to another (CLI wrapper).

Thin wrapper around :func:`hexa.workspace_copier.service.run_template_copy`.
Templates are server-wide, so this runs once per target server, independently of
any workspace copy. Both sides are remote: each needs a GraphQL URL and a
ServiceAccount token, sent as an ``Authorization: Bearer`` header on every
request.
"""

from django.core.management.base import BaseCommand, CommandError

from hexa.workspace_copier.progress import StreamReporter
from hexa.workspace_copier.results import format_templates_summary
from hexa.workspace_copier.service import CredentialError, run_template_copy
from hexa.workspace_copier.templates import DEFAULT_SOURCE_URL
from hexa.workspace_copier.transport import GraphQLError


class Command(BaseCommand):
    help = "Copy all pipeline templates from one OpenHEXA server to another."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-url",
            default=DEFAULT_SOURCE_URL,
            help=f"Source GraphQL endpoint (default: {DEFAULT_SOURCE_URL}).",
        )
        parser.add_argument(
            "--source-token",
            required=True,
            help="ServiceAccount token for the source server.",
        )
        parser.add_argument(
            "--target-url",
            required=True,
            help="Target GraphQL endpoint.",
        )
        parser.add_argument(
            "--target-token",
            required=True,
            help="ServiceAccount token for the target server.",
        )
        parser.add_argument(
            "--target-organization",
            required=True,
            help="UUID of the organization on the target server. The host "
            "'Template pipelines' workspace is created under it when needed.",
        )

    def handle(self, *args, **options):
        reporter = StreamReporter(self.stdout)

        try:
            result = run_template_copy(
                source_url=options["source_url"],
                source_token=options["source_token"],
                target_url=options["target_url"],
                target_token=options["target_token"],
                target_organization_id=options["target_organization"],
                reporter=reporter,
            )
        except CredentialError as exc:
            raise CommandError(
                "Endpoint verification failed:\n"
                + "\n".join(f"  - {e}" for e in exc.errors)
            )
        except GraphQLError as exc:
            raise CommandError(str(exc))

        self.stdout.write(format_templates_summary(result))
