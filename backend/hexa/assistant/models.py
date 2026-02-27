from django.contrib.auth import get_user_model
from django.db import models

from hexa.core.models.base import Base, BaseQuerySet
from hexa.core.models.soft_delete import (
    DefaultSoftDeletedManager,
    IncludeSoftDeletedManager,
    SoftDeletedModel,
    SoftDeleteQuerySet,
)
from hexa.workspaces.models import Workspace

User = get_user_model()


class ConversationQuerySet(BaseQuerySet, SoftDeleteQuerySet):
    def filter_for_user(self, user):
        return self._filter_for_user_and_query_object(
            user,
            models.Q(user=user, workspace__members=user),
        )


class Conversation(SoftDeletedModel, Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    model = models.CharField(max_length=200, null=False)
    total_input_tokens = models.IntegerField(default=0)
    total_output_tokens = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=12, decimal_places=6, default=0)

    # Full Pydantic AI message history for reconstructing agent context
    messages_history = models.JSONField(default=list)

    objects = DefaultSoftDeletedManager.from_queryset(ConversationQuerySet)()
    all_objects = IncludeSoftDeletedManager.from_queryset(ConversationQuerySet)()

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation({self.id}, user={self.user_id}, workspace={self.workspace_id})"


class Message(Base):
    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField()
    input_tokens = models.IntegerField(null=True, blank=True)
    output_tokens = models.IntegerField(null=True, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message({self.id}, role={self.role})"


class ToolInvocation(Base):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="tool_invocations"
    )
    tool_call_id = models.CharField(max_length=200)
    tool_name = models.CharField(max_length=200)
    tool_input = models.JSONField()
    tool_output = models.JSONField(null=True, blank=True)
    success = models.BooleanField(default=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"ToolInvocation({self.id}, tool={self.tool_name})"
