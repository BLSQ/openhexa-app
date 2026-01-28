from django.contrib import admin

from .models import Conversation, Message, ToolExecution


class MessageInline(admin.TabularInline):
    model = Message
    readonly_fields = ("id", "role", "content", "input_tokens", "output_tokens", "cost", "created_at")
    extra = 0
    can_delete = False


class ToolExecutionInline(admin.TabularInline):
    model = ToolExecution
    readonly_fields = ("id", "tool_name", "tool_input", "tool_output", "success", "created_at")
    extra = 0
    can_delete = False


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "workspace", "total_input_tokens", "total_output_tokens", "estimated_cost", "created_at", "updated_at")
    list_filter = ("workspace",)
    search_fields = ("id", "user__email", "workspace__name")
    readonly_fields = ("id", "total_input_tokens", "total_output_tokens", "estimated_cost")
    inlines = [MessageInline, ToolExecutionInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "role", "short_content", "input_tokens", "output_tokens", "cost", "created_at")
    list_filter = ("role",)
    search_fields = ("id", "content")

    @admin.display(description="Content")
    def short_content(self, obj):
        return obj.content[:100]


@admin.register(ToolExecution)
class ToolExecutionAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "tool_name", "success", "created_at")
    list_filter = ("tool_name", "success")
    search_fields = ("id", "tool_name")
