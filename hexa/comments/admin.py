from django.contrib import admin
from hexa.comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "submit_date", "content_object")
    search_fields = ("user.name",)
