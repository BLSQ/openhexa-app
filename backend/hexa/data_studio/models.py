import secrets

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.core.validators import validate_slug
from django.db import models
from slugify import slugify

from hexa.core.models.base import Base, BaseQuerySet
from hexa.databases.query_text import sanitize_sql
from hexa.user_management.models import User, UserInterface
from hexa.workspaces.models import Workspace

SLUG_MAX_LENGTH = 255


def generate_saved_query_slug(name: str, workspace: Workspace) -> str:
    """Build a slug unique within ``workspace``, suffixing on collision."""
    suffix = ""
    while True:
        # A name made only of characters slugify drops (punctuation, emoji)
        # leaves nothing to build on, and an empty slug would make the query
        # unaddressable by the endpoints keyed on it.
        slug = slugify(name[: SLUG_MAX_LENGTH - len(suffix)] + suffix) or "query"
        if not SavedQuery.objects.filter(workspace=workspace, slug=slug).exists():
            return slug
        suffix = "-" + secrets.token_hex(3)


class SavedQueryQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | UserInterface) -> models.QuerySet:
        return self.filter(workspace__in=Workspace.objects.filter_for_user(user))


class SavedQueryManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        workspace: Workspace,
        *,
        name: str,
        content: str,
        description: str = "",
    ):
        if not principal.has_perm("data_studio.create_saved_query", workspace):
            raise PermissionDenied

        return self.create(
            workspace=workspace,
            created_by=principal,
            name=name,
            content=content,
            description=description,
        )


class SavedQuery(Base):
    """A SQL query saved by a user in the Data Studio, shared with the whole workspace."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="saved_queries",
    )
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, null=False, blank=False)
    # Stable public identifier: web apps address a saved query by slug, so it is
    # generated once and left alone when the query is renamed.
    slug = models.CharField(
        max_length=SLUG_MAX_LENGTH, editable=False, validators=[validate_slug]
    )
    description = models.TextField(blank=True, default="")
    content = models.TextField()

    objects = SavedQueryManager.from_queryset(SavedQueryQuerySet)()

    class Meta:
        verbose_name_plural = "saved queries"
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                "workspace_id",
                "slug",
                name="unique_saved_query_slug_per_workspace",
            )
        ]
        indexes = [
            # `id` mirrors the tiebreaker the listing resolver appends: without it
            # Postgres can only presort on the leading column and still has to run an
            # incremental sort on top of the index scan.
            models.Index(
                fields=["workspace", "-updated_at", "id"],
                name="data_studio_ws_updated_idx",
            ),
            models.Index(
                fields=["workspace", "name", "id"],
                name="data_studio_ws_name_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        # SQL pasted from a chat, a document or a PDF carries blanks PostgreSQL
        # rejects; cleaning them here means a query is stored runnable whichever
        # way it was written (editor, admin, ...).
        self.content = sanitize_sql(self.content)
        # Generated here rather than in the manager (as pipelines do) because the
        # Django admin creates saved queries through a plain form, which would
        # otherwise hit the not-null column with nothing in it.
        if not self.slug:
            self.slug = generate_saved_query_slug(self.name, self.workspace)
        return super().save(*args, **kwargs)

    def update_if_has_perm(self, principal: User, **kwargs):
        if not principal.has_perm("data_studio.update_saved_query", self):
            raise PermissionDenied

        for key in ["name", "content"]:
            if kwargs.get(key) is not None:
                setattr(self, key, kwargs[key])

        # description is optional/blankable: an explicit null clears it, mirroring create.
        if "description" in kwargs:
            self.description = kwargs["description"] or ""

        return self.save()

    def delete_if_has_perm(self, principal: User):
        if not principal.has_perm("data_studio.delete_saved_query", self):
            raise PermissionDenied

        return self.delete()


class QueryLogQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | UserInterface) -> models.QuerySet:
        return self._filter_for_user_and_query_object(
            user,
            models.Q(workspace__in=Workspace.objects.filter_for_user(user)),
        )


class QueryLog(Base):
    """Audit log entry for a query executed against a data source via the API."""

    # SQLSTATE code reported for a successfully completed statement
    # (https://www.postgresql.org/docs/current/errcodes-appendix.html)
    SQLSTATE_SUCCESS = "00000"

    class Status(models.TextChoices):
        SUCCESS = "SUCCESS"
        # The query reached the data source but failed (invalid SQL, timeout, ...)
        ERROR = "ERROR"
        # The user was not allowed to run queries against the target
        DENIED = "DENIED"
        # The query was rejected before reaching the data source (e.g. multiple statements)
        REJECTED = "REJECTED"

    class Origin(models.TextChoices):
        # The client did not identify itself; every query arrives through the API anyway
        OTHER = "OTHER"
        DATA_STUDIO = "DATA_STUDIO"
        # Set server-side from the request, never accepted from a client: it is
        # the only origin that carries a security meaning (a web app can run
        # stored queries and nothing else).
        WEBAPP = "WEBAPP"

    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="query_logs"
    )
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="query_logs",
    )
    query = models.TextField()
    # Set when the SQL came from a stored query rather than from the caller, so
    # the audit trail answers "which saved query ran" and not only "what SQL ran".
    saved_query = models.ForeignKey(
        SavedQuery,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="query_logs",
    )
    status = models.CharField(max_length=10, choices=Status.choices)
    # SQLSTATE error code (https://www.postgresql.org/docs/current/errcodes-appendix.html);
    # SQLSTATE_SUCCESS on success, null when the query never reached the data source
    result_code = models.CharField(max_length=5, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True)
    row_count = models.PositiveIntegerField(null=True)
    truncated = models.BooleanField(default=False)
    origin = models.CharField(
        max_length=20, choices=Origin.choices, default=Origin.OTHER
    )
    # Free-text identifier of what was queried (e.g. "workspace_database"),
    # kept as plain text rather than choices so new source types don't need a migration.
    target = models.TextField()

    objects = QueryLogQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["origin"]),
            models.Index(fields=["target"]),
        ]

    def __str__(self) -> str:
        return f"{self.workspace.slug} - {self.status} - {self.created_at:%Y-%m-%d %H:%M:%S}"
