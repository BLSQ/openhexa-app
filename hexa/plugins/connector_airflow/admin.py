from django.contrib import admin
from django.contrib.admin import display
from django.utils.html import format_html

from .models import DAG, Cluster, ClusterPermission, DAGConfig, DAGRun


class PermissionInline(admin.StackedInline):
    extra = 1
    model = ClusterPermission


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ("name", "get_url")

    inlines = [
        PermissionInline,
    ]

    @display(ordering="url", description="Url")
    def get_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.url)


@admin.register(ClusterPermission)
class ClusterPermissionAdmin(admin.ModelAdmin):
    list_display = ("cluster", "team")


@admin.register(DAG)
class DAGAdmin(admin.ModelAdmin):
    list_display = ("dag_id", "cluster")


@admin.register(DAGConfig)
class DAGConfigAdmin(admin.ModelAdmin):
    list_display = ("name", "dag", "get_cluster")

    @display(ordering="dag__cluster", description="Cluster")
    def get_cluster(self, obj):
        return obj.dag.cluster


@admin.register(DAGRun)
class DAGRunAdmin(admin.ModelAdmin):
    list_display = ("run_id", "state", "execution_date", "dag", "get_cluster")

    @display(ordering="dag__cluster", description="Cluster")
    def get_cluster(self, obj):
        return obj.dag.cluster
