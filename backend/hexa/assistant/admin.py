from django.contrib import admin

from hexa.assistant.models import Conversation, Message, ToolInvocation
from hexa.utils.format import format_cost


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "workspace", "display_cost", "created_at", "updated_at")
    list_filter = ("workspace",)
    search_fields = ("id", "name", "user__email")
    raw_id_fields = ("user", "workspace")

    def display_cost(self, conversation: Conversation):
        return format_cost(conversation.cost)
    display_cost.short_description = "Cost"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("id", "conversation__id")
    raw_id_fields = ("conversation",)


@admin.register(ToolInvocation)
class ToolInvocationAdmin(admin.ModelAdmin):
    list_display = ("message", "tool_name", "success", "created_at")
    list_filter = ("tool_name", "success")
    search_fields = ("id", "message__id", "tool_name")
    raw_id_fields = ("message",)
