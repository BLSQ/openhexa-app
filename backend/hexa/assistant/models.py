from functools import cached_property

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import models

from hexa.assistant.instructions import InstructionSet
from hexa.assistant.types import MessageSegment, MessageSegmentAdapter
from hexa.core.models.base import Base, BaseQuerySet
from hexa.core.models.soft_delete import (
    DefaultSoftDeletedManager,
    IncludeSoftDeletedManager,
    SoftDeletedModel,
    SoftDeleteQuerySet,
)
from hexa.user_management.models import Organization, User
from hexa.workspaces.models import Workspace

CONVERSATION_NAME_MAX_LENGTH = 50


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
        linked_object=None,
    ):
        if not principal.has_perm("assistant.create_conversation", workspace):
            raise PermissionDenied

        conversation = self.model(
            user=principal,
            workspace=workspace,
            instruction_set=instruction_set,
        )
        if linked_object is not None:
            conversation.linked_object = linked_object
        conversation.save()
        return conversation


class Conversation(SoftDeletedModel, Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    linked_object_content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    linked_object_id = models.UUIDField(null=True, blank=True)
    linked_object = GenericForeignKey("linked_object_content_type", "linked_object_id")
    name = models.CharField(
        max_length=CONVERSATION_NAME_MAX_LENGTH, null=True, blank=True
    )
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
            # Covers the workspace conversation list query: filter_for_user().filter(workspace=workspace)
            # Leading with workspace allows efficient filtering when both workspace and user are known.
            models.Index(
                fields=["workspace", "user", "-updated_at"],
                name="asst_conv_list_idx",
            ),
            # Covers "find all conversations for a given linked object" queries.
            # Django does not auto-index GenericForeignKey fields.
            models.Index(
                fields=["linked_object_content_type", "linked_object_id"],
                name="asst_conv_linked_object_idx",
            ),
        ]

    @cached_property
    def agent(self):
        from hexa.assistant.agents import create_agent

        return create_agent(self)

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
    content = models.JSONField()
    input_tokens = models.IntegerField(null=True, blank=True)
    output_tokens = models.IntegerField(null=True, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            # Covers two queries:
            # 1. Organization.get_monthly_ai_cost(): nested loop over the organization's
            #    conversations, filtering by role='assistant' and created_at range, reading
            #    cost from INCLUDE.
            # 2. conversation.messages.filter(role="assistant").last() in mutations.py,
            #    which needs (conversation, role) as the leading columns.
            models.Index(
                fields=["conversation", "role", "-created_at"],
                include=["cost"],
                name="assistant_message_cost_idx",
            ),
            # Covers paginated message listing: conversation.messages.all() ordered by -created_at.
            # assistant_message_cost_idx cannot serve this efficiently because role sits between
            # conversation and created_at, preventing ordered reads without a sort.
            models.Index(
                fields=["conversation", "-created_at"],
                name="asst_msg_pagination_idx",
            ),
        ]

    @property
    def content_segments(self) -> list[MessageSegment]:
        return MessageSegmentAdapter.validate_python(self.content)

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
    proposal_pending = models.BooleanField(
        default=False,
        help_text=(
            "True while the proposal is awaiting user action; False once accepted or dismissed. "
            "Only meaningful for tool invocations that produce a user-facing proposal "
            "(e.g. propose_pipeline_version)."
        ),
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"ToolInvocation({self.id}, tool={self.tool_name})"


class AiUsage(Base):
    """A model call made on the organization's AI credentials outside the app's
    own agents: what the gateway runs for the AI tooling of its notebook
    servers, see `hexa.assistant.notebooks.gateway`.

    The app's agents keep their usage on the messages of a conversation; the
    organization's monthly AI cost sums both.
    """

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="ai_usages"
    )
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_usages",
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # Who the call was run for: "notebooks" for the gateway.
    source = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    # Input tokens include the prompt-cache ones, as genai_prices counts them.
    input_tokens = models.PositiveIntegerField(default=0)
    cache_read_tokens = models.PositiveIntegerField(default=0)
    cache_write_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    # In dollars; None when the model has no known price.
    cost = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    # When the call ended.
    occurred_at = models.DateTimeField()
    # The call's own id (the completion id the gateway answered with).
    external_id = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        ordering = ["-occurred_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "external_id"],
                condition=models.Q(external_id__isnull=False),
                name="assistant_ai_usage_unique_external_id",
            )
        ]
        indexes = [
            # Covers Organization.get_monthly_ai_cost().
            models.Index(
                fields=["organization", "occurred_at"],
                include=["cost"],
                name="asst_ai_usage_org_time_idx",
            ),
        ]

    def __str__(self):
        return f"AiUsage({self.id}, source={self.source}, model={self.model})"
