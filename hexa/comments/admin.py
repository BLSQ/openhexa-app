from django.contrib import admin
from hexa.comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "object", "created_at")
    search_fields = ("user.name",)
