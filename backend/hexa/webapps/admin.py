from django.contrib import admin

from hexa.webapps.models import SupersetWebapp, Webapp


@admin.register(Webapp)
class WebappAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "type", "is_public")
    list_filter = ("workspace", "type", "is_public")
    search_fields = ("id", "name")
    fields = (
        "name",
        "description",
        "workspace",
        "created_by",
        "url",
        "type",
        "is_public",
    )


class SupersetWebappInline(admin.StackedInline):
    model = SupersetWebapp
    extra = 0
    show_change_link = True
    fields = ("name", "workspace", "url")
    readonly_fields = ("name", "workspace", "url")


@admin.register(SupersetWebapp)
class SupersetWebappAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "is_public", "superset_dashboard")
    list_filter = ("workspace", "is_public")
    search_fields = ("id", "name")
    raw_id_fields = ("superset_dashboard",)
    fields = (
        "name",
        "description",
        "workspace",
        "created_by",
        "url",
        "is_public",
        "superset_dashboard",
    )
    readonly_fields = ("url",)
