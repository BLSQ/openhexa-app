from django.conf import settings
from django.db import models


class ToolCall(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tool_name = models.CharField(max_length=255, db_index=True)
    arguments = models.JSONField(default=dict)
    success = models.BooleanField()
    error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
