from django.contrib.auth.models import AnonymousUser
from django.db import models

from hexa.core.models.base import Base, BaseQuerySet
from hexa.user_management.models import UserInterface
from hexa.workspaces.models import Workspace


class DatabaseQueryLogQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | UserInterface) -> models.QuerySet:
        return self._filter_for_user_and_query_object(
            user,
            models.Q(workspace__in=Workspace.objects.filter_for_user(user)),
        )


class DatabaseQueryLog(Base):
    """Audit log entry for a SQL query executed against a workspace database via the API."""

    # SQLSTATE code reported for a successfully completed statement
    # (https://www.postgresql.org/docs/current/errcodes-appendix.html)
    SQLSTATE_SUCCESS = "00000"

    class Status(models.TextChoices):
        SUCCESS = "SUCCESS"
        # The query reached the database but failed (invalid SQL, timeout, ...)
        ERROR = "ERROR"
        # The user was not allowed to run queries against the workspace database
        DENIED = "DENIED"
        # The query was rejected before reaching the database (e.g. multiple statements)
        REJECTED = "REJECTED"

    class Origin(models.TextChoices):
        API = "API"
        DATA_STUDIO = "DATA_STUDIO"

    workspace = models.ForeignKey(
        "workspaces.Workspace", on_delete=models.CASCADE, related_name="query_logs"
    )
    user = models.ForeignKey(
        "user_management.User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="database_query_logs",
    )
    query = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices)
    # SQLSTATE error code (https://www.postgresql.org/docs/current/errcodes-appendix.html);
    # SQLSTATE_SUCCESS on success, null when the query never reached the database
    result_code = models.CharField(max_length=5, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True)
    row_count = models.PositiveIntegerField(null=True)
    truncated = models.BooleanField(default=False)
    origin = models.CharField(max_length=20, choices=Origin.choices, default=Origin.API)

    objects = DatabaseQueryLogQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.workspace.slug} - {self.status} - {self.created_at:%Y-%m-%d %H:%M:%S}"
