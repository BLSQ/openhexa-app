from django.db import models
from django.db.models import Q

from hexa.core.models.base import Base, BaseQuerySet
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace

ASSISTANT_MODELS = {
    "claude-sonnet-4-20250514": {
        "label": "Claude Sonnet 4",
        "input_price_per_million": 3.00,
        "output_price_per_million": 15.00,
    },
    "claude-opus-4-5-20251101": {
        "label": "Claude Opus 4.5",
        "input_price_per_million": 5.00,
        "output_price_per_million": 25.00,
    },
    "claude-haiku-3-5-20241022": {
        "label": "Claude Haiku 3.5",
        "input_price_per_million": 0.80,
        "output_price_per_million": 4.00,
    },
}
DEFAULT_ASSISTANT_MODEL = "claude-sonnet-4-20250514"


class ConversationQuerySet(BaseQuerySet):
    def filter_for_user(self, user):
        return self._filter_for_user_and_query_object(
            user,
            Q(user=user, workspace__members=user),
            return_all_if_superuser=True,
        )


class Conversation(Base):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="assistant_conversations"
    )
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="assistant_conversations"
    )

    model = models.CharField(max_length=100, default="")

    total_input_tokens = models.IntegerField(default=0)
    total_output_tokens = models.IntegerField(default=0)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    objects = ConversationQuerySet.as_manager()

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation {self.id} ({self.user})"


class Message(Base):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=10)
    content = models.TextField()

    input_tokens = models.IntegerField(null=True, blank=True)
    output_tokens = models.IntegerField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class ToolExecution(Base):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="tool_executions"
    )
    tool_name = models.CharField(max_length=100)
    tool_input = models.JSONField()
    tool_output = models.JSONField()
    success = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tool_name} ({'ok' if self.success else 'error'})"


class PendingToolApproval(Base):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="pending_approvals"
    )
    tool_use_id = models.CharField(max_length=100)
    tool_name = models.CharField(max_length=100)
    tool_input = models.JSONField()

    claude_response = models.JSONField()
    messages_snapshot = models.JSONField()

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )

    input_tokens_so_far = models.IntegerField(default=0)
    output_tokens_so_far = models.IntegerField(default=0)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"PendingToolApproval({self.tool_name}, {self.status})"
