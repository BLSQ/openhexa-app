from django.contrib import admin

from hexa.assistant.models import Conversation, Message, ToolInvocation


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "workspace", "model", "created_at", "updated_at")
    list_filter = ("workspace", "model")
    search_fields = ("id", "user__email")
    raw_id_fields = ("user", "workspace")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("id", "conversation__id")
    raw_id_fields = ("conversation",)


@admin.register(ToolInvocation)
class ToolInvocationAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "tool_name", "success", "created_at")
    list_filter = ("tool_name", "success")
    search_fields = ("id", "conversation__id", "tool_name")
    raw_id_fields = ("conversation",)
