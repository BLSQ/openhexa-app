import json

from django.contrib import admin
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html, mark_safe

from hexa.assistant.models import Conversation, Message, ToolInvocation
from hexa.utils.format import format_cost

TOKEN_ORANGE_THRESHOLD = 200_000
TOKEN_RED_THRESHOLD = 500_000
COST_ORANGE_THRESHOLD = 2
COST_RED_THRESHOLD = 10

WARNING_ORANGE_STYLE = (
    "background:#fff4e5;color:#b45309;border-radius:3px;padding:1px 4px;"
    "font-weight:bold"
)
WARNING_RED_STYLE = (
    "background:#ffefef;color:#ba2121;border-radius:3px;padding:1px 4px;"
    "font-weight:bold"
)

COST_TIERS = (
    (COST_RED_THRESHOLD, WARNING_RED_STYLE),
    (COST_ORANGE_THRESHOLD, WARNING_ORANGE_STYLE),
)
TOKEN_TIERS = (
    (TOKEN_RED_THRESHOLD, WARNING_RED_STYLE),
    (TOKEN_ORANGE_THRESHOLD, WARNING_ORANGE_STYLE),
)


def _format_with_warning(value, formatter, tiers):
    if value is None:
        return "—"
    text = formatter(value)
    for threshold, style in tiers:
        if value >= threshold:
            return format_html("<span style='{}'>{}</span>", style, text)
    return text


def format_cost_with_warning(cost):
    return _format_with_warning(cost, format_cost, COST_TIERS)


def format_token_count_with_warning(count):
    return _format_with_warning(count, "{:,}".format, TOKEN_TIERS)


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
    fields = (
        "role",
        "content",
        "display_input_tokens",
        "display_output_tokens",
        "display_cost",
        "created_at",
        "tool_invocations_link",
    )
    readonly_fields = fields
    can_delete = False
    show_change_link = True

    def display_input_tokens(self, message: Message):
        return format_token_count_with_warning(message.input_tokens)

    display_input_tokens.short_description = "Input tokens"

    def display_output_tokens(self, message: Message):
        return (
            f"{message.output_tokens:,}" if message.output_tokens is not None else "—"
        )

    display_output_tokens.short_description = "Output tokens"

    def display_cost(self, message: Message):
        return format_cost_with_warning(message.cost)

    display_cost.short_description = "Cost"

    def tool_invocations_link(self, message: Message):
        invocations = message.tool_invocations.all()
        if not invocations:
            return "—"
        items = mark_safe(
            "".join(
                format_html(
                    "<li><a href='{}'><img src='{}' alt='{}'> {}</a></li>",
                    reverse("admin:assistant_toolinvocation_change", args=[inv.pk]),
                    static("admin/img/icon-%s.svg" % ("yes" if inv.success else "no")),
                    inv.success,
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
        "display_total_input_tokens",
        "display_total_output_tokens",
        "cost",
        "messages_history_display",
    )
    readonly_fields = (
        "instruction_set",
        "display_total_input_tokens",
        "display_total_output_tokens",
        "cost",
        "messages_history_display",
    )
    list_filter = ("workspace",)
    search_fields = ("id", "name", "user__email")
    raw_id_fields = ("user", "workspace")
    inlines = [MessageInline]
    date_hierarchy = "updated_at"

    def display_cost(self, conversation: Conversation):
        return format_cost_with_warning(conversation.cost)

    display_cost.short_description = "Cost"

    def display_total_input_tokens(self, conversation: Conversation):
        return f"{conversation.total_input_tokens:,}"

    display_total_input_tokens.short_description = "Total input tokens"

    def display_total_output_tokens(self, conversation: Conversation):
        return f"{conversation.total_output_tokens:,}"

    display_total_output_tokens.short_description = "Total output tokens"

    def messages_history_display(self, conversation: Conversation):
        payload = json.dumps(conversation.messages_history, indent=2)
        # Rough context-size indication: ~4 chars per token, computed on the
        # compact serialization so pretty-printing whitespace doesn't inflate it.
        compact_size = len(
            json.dumps(conversation.messages_history, separators=(",", ":"))
        )
        token_estimate = compact_size // 4
        return format_html(
            "<details>"
            "<summary style='cursor:pointer'>{} messages ({} chars, ~{} tokens)</summary>"
            "<button type='button' onclick='navigator.clipboard.writeText("
            "this.nextElementSibling.textContent)'>Copy JSON</button>"
            "<pre style='max-height:30em;overflow:auto'>{}</pre>"
            "</details>",
            len(conversation.messages_history),
            f"{len(payload):,}",
            format_token_count_with_warning(token_estimate),
            payload,
        )

    messages_history_display.short_description = "Messages history"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "conversation",
        "role",
        "input_tokens",
        "output_tokens",
        "display_cost",
        "created_at",
    )
    list_filter = ("role",)
    search_fields = ("id", "conversation__id")
    raw_id_fields = ("conversation",)
    inlines = [ToolInvocationInline]

    def display_cost(self, message: Message):
        return format_cost_with_warning(message.cost)

    display_cost.short_description = "Cost"


@admin.register(ToolInvocation)
class ToolInvocationAdmin(admin.ModelAdmin):
    list_display = ("tool_name", "message", "success", "created_at")
    list_filter = ("tool_name", "success")
    search_fields = ("id", "message__id", "tool_name")
    raw_id_fields = ("message",)
