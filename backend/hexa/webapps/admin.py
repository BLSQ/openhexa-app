from django.contrib import admin

from hexa.webapps.models import GitWebapp, SupersetWebapp, Webapp


@admin.register(Webapp)
class WebappAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "subdomain", "workspace", "type", "is_public", "custom_domain")
    list_filter = ("workspace", "type", "is_public")
    search_fields = ("id", "name", "custom_domain")
    fields = (
        "name",
        "slug",
        "subdomain",
        "description",
        "workspace",
        "created_by",
        "url",
        "type",
        "is_public",
        "show_powered_by",
        "custom_domain",
    )
    readonly_fields = ("slug",)


@admin.register(GitWebapp)
class GitWebappAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "repository", "published_commit", "is_public", "custom_domain")
    list_filter = ("workspace",)
    search_fields = ("id", "name", "repository", "custom_domain")
    fields = (
        "name",
        "description",
        "workspace",
        "created_by",
        "repository",
        "published_commit",
        "is_public",
        "show_powered_by",
        "custom_domain",
    )
    readonly_fields = ("repository",)


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
        "show_powered_by",
        "superset_dashboard",
    )
    readonly_fields = ("url",)
