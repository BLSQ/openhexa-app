from datetime import timedelta

from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from hexa.assistant.instructions import InstructionSet
from hexa.core.models.base import Base, BaseQuerySet
from hexa.core.models.soft_delete import (
    DefaultSoftDeletedManager,
    IncludeSoftDeletedManager,
    SoftDeletedModel,
    SoftDeleteQuerySet,
)
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class ConversationQuerySet(BaseQuerySet, SoftDeleteQuerySet):
    def filter_for_user(self, user: User):
        return self._filter_for_user_and_query_object(
            user,
            models.Q(user=user, workspace__members=user),
        )


class ConversationManager(DefaultSoftDeletedManager):
    def create_if_has_perm(
        self,
        principal: User,
        workspace: Workspace,
        *,
        instruction_set: InstructionSet = InstructionSet.GENERAL,
    ):
        if not principal.has_perm("assistant.create_conversation", workspace):
            raise PermissionDenied

        return self.create(
            user=principal,
            workspace=workspace,
            instruction_set=instruction_set,
        )


class Conversation(SoftDeletedModel, Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    name = models.CharField(max_length=50, null=True, blank=True)
    instruction_set = models.CharField(
        max_length=50,
        choices=InstructionSet.choices,
        default=InstructionSet.GENERAL,
    )
    total_input_tokens = models.IntegerField(default=0)
    total_output_tokens = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=12, decimal_places=6, default=0)

    # Full Pydantic AI message history for reconstructing agent context
    messages_history = models.JSONField(default=list)

    objects = ConversationManager.from_queryset(ConversationQuerySet)()
    all_objects = IncludeSoftDeletedManager.from_queryset(ConversationQuerySet)()

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(
                fields=["workspace", "user", "-updated_at"],
                name="asst_conv_list_idx",
            ),
        ]

    def __str__(self):
        return f"Conversation({self.id}, user={self.user_id}, workspace={self.workspace_id})"

    @classmethod
    def get_monthly_cost_for_user(cls, user: User) -> float:
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_next_month = (start_of_month + timedelta(days=32)).replace(day=1)
        result = Message.objects.filter(
            conversation__user=user,
            role=Message.Role.ASSISTANT,
            created_at__gte=start_of_month,
            created_at__lt=start_of_next_month,
        ).aggregate(total=Sum("cost"))["total"]
        return float(result or 0)


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
        indexes = [
            models.Index(
                fields=["conversation", "role", "created_at"],
                include=["cost"],
                name="assistant_message_cost_idx",
            ),
            models.Index(
                fields=["conversation", "-created_at"],
                name="asst_msg_pagination_idx",
            ),
        ]

    def __str__(self):
        return f"Message({self.id}, role={self.role})"


class ToolInvocation(Base):
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="tool_invocations"
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
