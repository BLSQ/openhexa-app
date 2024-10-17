# Create your models here.

import logging

from django.db import models
from django.db.models import Q

from hexa.core.models import Base
from hexa.core.models.base import BaseQuerySet

logger = logging.getLogger(__name__)


class AuthType(models.TextChoices):
    PUBLIC = "public", "Public"
    WORKSPACE_USER = "workspace_user", "Workspace User"
    TOKEN = "token", "Token"


class FileAccessRuleQuerySet(BaseQuerySet):
    def filter_for_user(self, user):
        return self._filter_for_user_and_query_object(
            user,
            models.Q(workspace__members=user),
            return_all_if_superuser=False,
        )

    def is_active(self):
        return self.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gte=models.functions.Now())
        )

    def find_nearest_access(self, workspace, path: str):
        q = self.filter(workspace=workspace)

        # Split the URI by slashes
        path_parts = path.strip("/").split("/")

        # Build all possible prefixes from longest to shortest
        prefixes = []
        for i in range(len(path_parts), 0, -1):
            prefix = "/".join(path_parts[:i])
            prefixes.append(f"/{prefix}")

        # Query for the longest matching prefix in ExternalAccess
        for prefix in prefixes:
            try:
                match = q.filter(path=prefix).first()
                if match:
                    return match
            except FileAccessRule.DoesNotExist:
                continue

        # No match found
        return None


class FileAccessRule(Base):
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="files_access_rules",
    )
    path = models.TextField()  # Path to the file or directory
    description = models.TextField(null=True, blank=True)
    auth_type = models.CharField(
        max_length=20,
        choices=AuthType.choices,
        default=AuthType.PUBLIC,
    )
    created_by = models.ForeignKey(
        "user_management.User",
        null=True,
        on_delete=models.SET_NULL,
        related_name=None,
    )
    flagged = models.BooleanField(
        default=False
    )  # Flagged for review when no file or path in the bucket matches the path
    expires_at = models.DateTimeField(null=True, blank=True)
    token = models.CharField(max_length=100, null=True, blank=True)

    objects = FileAccessRuleQuerySet.as_manager()

    class Meta:
        unique_together = [["workspace", "path"]]
        ordering = ["-created_at"]
