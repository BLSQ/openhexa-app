from django.contrib import admin

from hexa.webapps.models import SupersetWebapp, Webapp


@admin.register(Webapp)
class WebappAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace")
    list_filter = ("workspace",)
    search_fields = ("id", "name")
    fields = ("name", "description", "workspace", "created_by", "url")

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(type=Webapp.WebappType.SUPERSET)


class SupersetWebappInline(admin.StackedInline):
    model = SupersetWebapp
    extra = 0
    show_change_link = True
    fields = ("name", "workspace", "url")
    readonly_fields = ("name", "workspace", "url")


@admin.register(SupersetWebapp)
class SupersetWebappAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "superset_dashboard")
    list_filter = ("workspace",)
    search_fields = ("id", "name")
    raw_id_fields = ("superset_dashboard",)
    fields = (
        "name",
        "description",
        "workspace",
        "created_by",
        "url",
        "superset_dashboard",
    )
    readonly_fields = ("url",)
