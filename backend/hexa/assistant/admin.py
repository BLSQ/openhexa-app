from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, mark_safe

from hexa.assistant.models import Conversation, Message, ToolInvocation
from hexa.utils.format import format_cost


class ToolInvocationInline(admin.TabularInline):
    model = ToolInvocation
    extra = 0
    readonly_fields = (
        "tool_call_id",
        "tool_name",
        "tool_input",
        "tool_output",
        "success",
        "created_at",
    )
    can_delete = False


class MessageInline(admin.StackedInline):
    model = Message
    extra = 0
    fields = ("role", "content", "created_at", "tool_invocations_link")
    readonly_fields = ("role", "content", "created_at", "tool_invocations_link")
    can_delete = False
    show_change_link = True

    def tool_invocations_link(self, message: Message):
        invocations = message.tool_invocations.all()
        if not invocations:
            return "—"
        items = mark_safe(
            "".join(
                format_html(
                    "<li><a href='{}'>{}</a></li>",
                    reverse("admin:assistant_toolinvocation_change", args=[inv.pk]),
                    inv.tool_name,
                )
                for inv in invocations
            )
        )
        return format_html("<ul style='margin:0;padding-left:1em'>{}</ul>", items)

    tool_invocations_link.short_description = "Tool invocations"


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "workspace",
        "display_cost",
        "created_at",
        "updated_at",
    )
    fields = (
        "name",
        "user",
        "workspace",
        "deleted_at",
        "restored_at",
        "instruction_set",
        "total_input_tokens",
        "total_output_tokens",
        "cost",
    )
    readonly_fields = (
        "instruction_set",
        "total_input_tokens",
        "total_output_tokens",
        "cost",
    )
    list_filter = ("workspace",)
    search_fields = ("id", "name", "user__email")
    raw_id_fields = ("user", "workspace")
    inlines = [MessageInline]

    def display_cost(self, conversation: Conversation):
        return format_cost(conversation.cost)

    display_cost.short_description = "Cost"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("id", "conversation__id")
    raw_id_fields = ("conversation",)
    inlines = [ToolInvocationInline]


@admin.register(ToolInvocation)
class ToolInvocationAdmin(admin.ModelAdmin):
    list_display = ("message", "tool_name", "success", "created_at")
    list_filter = ("tool_name", "success")
    search_fields = ("id", "message__id", "tool_name")
    raw_id_fields = ("message",)
