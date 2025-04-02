from django.conf import settings
from django.contrib import admin
from django.contrib.admin import display
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html

from hexa.pipelines.queue import environment_sync_queue

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


class DAGAuthorizedDatasourceInline(admin.TabularInline):
    extra = 1
    model = DAGAuthorizedDatasource
    verbose_name = "Authorized Datasource"


@admin.action(description="Sync selected Airflow cluster(s)")
def SyncCluster(modeladmin: admin.ModelAdmin, request, queryset):
    for cluster in list(queryset):
        if settings.EXTERNAL_ASYNC_REFRESH:
            environment_sync_queue.enqueue(
                "environment_sync",
                {
                    "contenttype_id": str(
                        ContentType.objects.get_for_model(cluster).id
                    ),
                    "object_id": str(cluster.id),
                },
            )
            modeladmin.message_user(request, "The environment will soon be synced")
        else:
            try:
                sync_result = cluster.sync()
                modeladmin.message_user(request, sync_result)
            except Exception:
                modeladmin.message_user(
                    request, f"Sync failed for environment {cluster.id}"
                )


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ("name", "get_url", "last_synced_at", "auto_sync")
    actions = [SyncCluster]

    @display(ordering="url", description="Url")
    def get_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.url)


@admin.register(DAGTemplate)
class DAGTemplateAdmin(admin.ModelAdmin):
    list_display = ("code", "cluster")


@admin.register(DAG)
class DAGAdmin(admin.ModelAdmin):
    list_display = ("dag_id", "template", "schedule", "user")
    list_filter = ("template",)
    search_fields = ("dag_id",)

    inlines = [PermissionInline, DAGAuthorizedDatasourceInline]


@admin.register(DAGRun)
class DAGRunAdmin(admin.ModelAdmin):
    list_display = ("run_id", "state", "execution_date", "dag", "get_cluster")
    list_filter = ("state", "execution_date", "dag", "dag__template__cluster")

    @display(ordering="dag__template__cluster", description="Cluster")
    def get_cluster(self, obj: DAGRun):
        return obj.dag.template.cluster


@admin.register(DAGAuthorizedDatasource)
class DAGAuthorizedDatasourceAdmin(admin.ModelAdmin):
    list_display = ("dag", "datasource", "connector", "slug")
    search_fields = ("dag__dag_id",)

    @admin.display(
        ordering="datasource_type__app_label",
    )
    def connector(self, instance):
        return instance.datasource_type.app_label


@admin.register(DAGPermission)
class DAGPermissionAdmin(admin.ModelAdmin):
    list_display = ("dag", "team", "user", "mode")
