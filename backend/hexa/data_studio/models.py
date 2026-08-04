from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import models
from django.utils.translation import gettext_lazy as _

from hexa.core.models.base import Base, BaseQuerySet
from hexa.databases.query_text import sanitize_sql
from hexa.user_management.models import ServicePrincipal, User, UserInterface
from hexa.workspaces.models import Workspace


class SavedQueryVisibility(models.TextChoices):
    PRIVATE = "PRIVATE", _("Private")
    WORKSPACE = "WORKSPACE", _("Workspace")


class SavedQueryQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | UserInterface) -> models.QuerySet:
        accessible = models.Q(visibility=SavedQueryVisibility.WORKSPACE)
        # Service principals (pipeline runs, webapps) impersonate a workspace rather
        # than a person, so they never own a private query - and `created_by=<principal>`
        # would not even be a valid lookup for them.
        if isinstance(user, User) and not isinstance(user, ServicePrincipal):
            accessible |= models.Q(created_by=user)

        return self._filter_for_user_and_query_object(
            user,
            models.Q(workspace__in=Workspace.objects.filter_for_user(user))
            & accessible,
        )


class SavedQueryManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        workspace: Workspace,
        *,
        name: str,
        content: str,
        description: str = "",
        # None means "unspecified" and lands on the default: a brand-new query is
        # private until its author decides to share it.
        visibility: str | None = None,
    ):
        if not principal.has_perm("data_studio.create_saved_query", workspace):
            raise PermissionDenied

        return self.create(
            workspace=workspace,
            created_by=principal,
            name=name,
            content=content,
            description=description,
            visibility=visibility or SavedQueryVisibility.PRIVATE,
        )


class SavedQuery(Base):
    """A SQL query saved by a user in the Data Studio.

    A saved query belongs to a workspace, but its `visibility` decides who within
    that workspace can reach it: WORKSPACE queries are shared with every member,
    PRIVATE ones are the author's alone.
    """

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="saved_queries",
    )
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(blank=True, default="")
    content = models.TextField()
    visibility = models.CharField(
        max_length=20,
        choices=SavedQueryVisibility.choices,
        default=SavedQueryVisibility.PRIVATE,
    )

    objects = SavedQueryManager.from_queryset(SavedQueryQuerySet)()

    class Meta:
        verbose_name_plural = "saved queries"
        ordering = ["-updated_at"]
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
            # Listings match `workspace = X AND (visibility = 'WORKSPACE' OR
            # created_by = me)`. Postgres serves that OR as a BitmapOr, so the two
            # indexes above cover the shared branch and this one covers the author
            # branch. `visibility` is deliberately not folded into their leading
            # columns: a BitmapOr discards index ordering anyway, so it would buy
            # nothing. If this ever shows up in profiling, the next step is partial
            # indexes, not a reshuffle here.
            models.Index(
                fields=["workspace", "created_by", "-updated_at", "id"],
                name="data_studio_ws_author_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        # SQL pasted from a chat, a document or a PDF carries blanks PostgreSQL
        # rejects; cleaning them here means a query is stored runnable whichever
        # way it was written (editor, admin, ...).
        self.content = sanitize_sql(self.content)
        return super().save(*args, **kwargs)

    def update_if_has_perm(self, principal: User, **kwargs):
        if not principal.has_perm("data_studio.update_saved_query", self):
            raise PermissionDenied

        # Sharing is gated separately from the rest of the attributes, and only when
        # it actually changes: a client echoing back the current visibility must not
        # need the stricter permission.
        visibility = kwargs.get("visibility")
        if visibility is not None and visibility != self.visibility:
            if not principal.has_perm(
                "data_studio.update_saved_query_visibility", self
            ):
                raise PermissionDenied
            self.visibility = visibility

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
