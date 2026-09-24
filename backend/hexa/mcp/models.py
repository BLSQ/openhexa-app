from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from oauth2_provider.models import AccessToken, Grant, RefreshToken

from hexa.core.models.base import Base
from hexa.user_management.models import ServicePrincipal, User


class MCPResource(models.TextChoices):
    WORKSPACES = "WORKSPACES", "Workspaces"
    FILES = "FILES", "Files"
    DATASETS = "DATASETS", "Datasets"
    PIPELINES = "PIPELINES", "Pipelines"
    TEMPLATES = "TEMPLATES", "Pipeline templates"
    WEBAPPS = "WEBAPPS", "Web apps"
    DATABASES = "DATABASES", "Databases"
    CONNECTIONS = "CONNECTIONS", "Connections"


class MCPConnection(Base):
    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                "user", "application", name="mcp_connection_unique_user_application"
            )
        ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mcp_connections",
    )
    application = models.ForeignKey(
        "oauth2_provider.Application",
        on_delete=models.CASCADE,
        related_name="mcp_connections",
    )
    workspaces = models.ManyToManyField(
        "workspaces.Workspace", blank=True, related_name="mcp_connections"
    )
    tools = models.JSONField(default=list)
    last_used_at = models.DateTimeField(null=True, blank=True)

    def mark_used(self) -> None:
        MCPConnection.objects.filter(pk=self.pk).update(last_used_at=timezone.now())

    def allows_tool(self, name: str) -> bool:
        return name in self.tools

    def supersede_earlier_registrations(self) -> int:
        superseded = MCPConnection.objects.filter(
            user=self.user, application__name=self.application.name
        ).exclude(pk=self.pk)
        applications = [connection.application_id for connection in superseded]
        if not applications:
            return 0

        token_filter = {"user": self.user, "application_id__in": applications}
        with transaction.atomic():
            RefreshToken.objects.filter(**token_filter).delete()
            AccessToken.objects.filter(**token_filter).delete()
            Grant.objects.filter(**token_filter).delete()
            count, _ = superseded.delete()
        return count


class MCPUser(User, ServicePrincipal):
    class Meta:
        proxy = True

    connection = None
    real_user = None

    @classmethod
    def from_user(cls, user: User, connection: MCPConnection) -> "MCPUser":
        instance = cls.objects.get(pk=user.pk)
        instance.connection = connection
        instance.real_user = user
        return instance

    @property
    def workspace_ids(self):
        return list(self.connection.workspaces.values_list("id", flat=True))

    def get_username(self):
        return f"mcp_{self.connection.application_id}_as_{self.email}"


class ToolCall(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tool_name = models.CharField(max_length=255, db_index=True)
    arguments = models.JSONField(default=dict)
    success = models.BooleanField()
    error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
