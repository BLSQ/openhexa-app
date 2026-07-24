from django.contrib import admin

from .models import QueryLog


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ("workspace", "user", "status", "origin", "target", "created_at")
    list_select_related = ("workspace", "user")
    list_filter = ("status", "origin", "target", "workspace")
    search_fields = ("workspace__slug", "workspace__name", "user__email", "query")
    date_hierarchy = "created_at"
    readonly_fields = [f.name for f in QueryLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
