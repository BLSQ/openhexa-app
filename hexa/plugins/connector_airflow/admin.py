from django.contrib import admin
from django.contrib.admin import display
from django.utils.html import format_html

from .models import (
    DAG,
    Cluster,
    DAGAuthorizedDatasource,
    DAGPermission,
    DAGRun,
    DAGTemplate,
)


class PermissionInline(admin.StackedInline):
    extra = 1
    model = DAGPermission
    verbose_name = "Team permission"


class DAGAuthorizedDatasourceInline(admin.TabularInline):
    extra = 1
    model = DAGAuthorizedDatasource
    verbose_name = "Authorized Datasource"


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ("name", "get_url", "last_synced_at", "auto_sync")

    @display(ordering="url", description="Url")
    def get_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.url)


@admin.register(DAGPermission)
class DAGPermissionAdmin(admin.ModelAdmin):
    list_display = ("dag", "team")


@admin.register(DAGTemplate)
class DAGTemplateAdmin(admin.ModelAdmin):
    list_display = ("cluster", "code")


@admin.register(DAG)
class DAGAdmin(admin.ModelAdmin):
    list_display = ("dag_id", "template", "schedule", "user")

    inlines = [PermissionInline, DAGAuthorizedDatasourceInline]


@admin.register(DAGRun)
class DAGRunAdmin(admin.ModelAdmin):
    list_display = ("run_id", "state", "execution_date", "dag", "get_cluster")

    @display(ordering="dag__template__cluster", description="Cluster")
    def get_cluster(self, obj: DAGRun):
        return obj.dag.template.cluster


@admin.register(DAGAuthorizedDatasource)
class DAGAuthorizedDatasourceAdmin(admin.ModelAdmin):
    list_display = ("dag", "datasource", "connector", "slug")

    @admin.display(
        ordering="datasource_type__app_label",
    )
    def connector(self, instance):
        return instance.datasource_type.app_label
