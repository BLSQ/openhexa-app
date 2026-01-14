import uuid

from django.conf import settings
from django.db import models

from hexa.workspaces.models import Workspace


class DatasetRecipe(models.Model):
    """
    SQL recipe stored in the OpenHexa (Django) database, scoped to a workspace.

    This is the source of truth. It can be executed on-demand against the workspace DB.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="dataset_recipes",
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")

    # Parameterized SQL template (SELECT-only). See utils.render_recipe_sql
    sql_template = models.TextField()

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_dataset_recipes",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_dataset_recipes",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("workspace", "name")]
        indexes = [
            models.Index(fields=["workspace", "is_active"]),
        ]

    def __str__(self):
        return f"{self.workspace.slug}::{self.name}"
