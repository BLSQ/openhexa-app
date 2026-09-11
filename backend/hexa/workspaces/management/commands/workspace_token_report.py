"""Report on how workspace tokens are being used (HEXA-1775 phase 0).

Answers the question: of the tokens actually in use,
how many ever reach out of scope?
"""

from collections import Counter, defaultdict
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone

from hexa.workspaces.models import TokenScopeVerdict, Workspace, WorkspaceTokenUsage


def token_key(row: dict) -> tuple:
    """Identity of the token a usage row belongs to.

    Membership tokens are stable, so their fingerprint is the token. Identity
    tokens are change per notebook session, so counting fingerprints would
    count sessions; they are grouped by the (user, workspace) pair they stand for.
    """
    if row["token_type"] == "membership":
        return ("membership", row["token_fingerprint"])
    return (row["token_type"], row["user_id"], row["workspace_id"])


class Command(BaseCommand):
    help = "Summarise workspace token usage collected by the scope audit."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=30)
        parser.add_argument(
            "--per-token",
            action="store_true",
            help="List the tokens that reached outside their workspace.",
        )
        parser.add_argument(
            "--prune",
            action="store_true",
            help="Delete usage records older than --days instead of reporting.",
        )

    def handle(self, *args, days: int, per_token: bool, prune: bool, **options):
        since = timezone.now() - timedelta(days=days)

        if prune:
            deleted, _ = WorkspaceTokenUsage.objects.filter(
                created_at__lt=since
            ).delete()
            self.stdout.write(f"Deleted {deleted} usage records older than {days}d.")
            return

        rows = (
            WorkspaceTokenUsage.objects.filter(created_at__gte=since)
            .values(
                "token_type", "token_fingerprint", "user_id", "workspace_id", "verdict"
            )
            .annotate(requests=Count("id"))
        )

        tokens = defaultdict(Counter)
        for row in rows:
            tokens[token_key(row)][row["verdict"]] += row["requests"]

        if not tokens:
            self.stdout.write(f"No workspace token usage recorded in the last {days}d.")
            return

        self._write_summary(tokens, days)
        self._write_operations(since)
        self._write_organizations(since)
        if per_token:
            self._write_offenders(since)

    def _write_summary(self, tokens: dict, days: int):
        out_of_scope = {
            key: counts
            for key, counts in tokens.items()
            if counts[TokenScopeVerdict.OUT_OF_SCOPE]
        }
        cross_reachable = {
            key: counts
            for key, counts in tokens.items()
            if counts[TokenScopeVerdict.CROSS_REACHABLE] and key not in out_of_scope
        }
        requests = sum(sum(counts.values()) for counts in tokens.values())
        broken = sum(
            counts[TokenScopeVerdict.OUT_OF_SCOPE] for counts in tokens.values()
        )

        self.stdout.write(f"\nWorkspace token usage — last {days} days\n")
        self.stdout.write(f"  active tokens              {len(tokens)}")
        self.stdout.write(
            f"  would break if scoped      {len(out_of_scope)} "
            f"({self._share(len(out_of_scope), len(tokens))})"
        )
        self.stdout.write(
            f"  cross-workspace but legal  {len(cross_reachable)} "
            f"({self._share(len(cross_reachable), len(tokens))})"
        )
        self.stdout.write(f"\n  requests                   {requests}")
        self.stdout.write(
            f"  out-of-scope requests      {broken} ({self._share(broken, requests)})"
        )

    def _write_operations(self, since):
        counter = Counter()
        for row in WorkspaceTokenUsage.objects.filter(
            created_at__gte=since, verdict=TokenScopeVerdict.OUT_OF_SCOPE
        ).values_list("root_fields", flat=True):
            counter.update(row)
        if counter:
            self.stdout.write("\n  out-of-scope operations")
            for field, count in counter.most_common(15):
                self.stdout.write(f"    {count:>8}  {field}")

    def _write_organizations(self, since):
        rows = (
            WorkspaceTokenUsage.objects.filter(created_at__gte=since)
            .values("workspace_id", "verdict")
            .annotate(requests=Count("id"))
        )
        by_workspace = defaultdict(Counter)
        for row in rows:
            by_workspace[row["workspace_id"]][row["verdict"]] += row["requests"]

        organizations = defaultdict(Counter)
        for workspace in Workspace.objects.filter(pk__in=by_workspace).select_related(
            "organization"
        ):
            name = workspace.organization.name if workspace.organization else "—"
            organizations[name] += by_workspace[workspace.pk]

        self.stdout.write("\n  by organization (out-of-scope / total requests)")
        for name, counts in sorted(
            organizations.items(),
            key=lambda item: -item[1][TokenScopeVerdict.OUT_OF_SCOPE],
        ):
            total = sum(counts.values())
            self.stdout.write(
                f"    {counts[TokenScopeVerdict.OUT_OF_SCOPE]:>6} / {total:<6}  {name}"
            )

    def _write_offenders(self, since):
        rows = (
            WorkspaceTokenUsage.objects.filter(
                created_at__gte=since, verdict=TokenScopeVerdict.OUT_OF_SCOPE
            )
            .values("token_fingerprint", "token_type", "user__email", "workspace__slug")
            .annotate(requests=Count("id"))
            .order_by("-requests")
        )
        self.stdout.write("\n  tokens reaching outside their workspace")
        for row in rows:
            self.stdout.write(
                f"    {row['requests']:>6}  {row['token_fingerprint'][:8]}  "
                f"{row['token_type']:<10}  {row['user__email']}  → {row['workspace__slug']}"
            )

    @staticmethod
    def _share(part: int, total: int) -> str:
        return f"{(100 * part / total):.1f}%" if total else "—"
