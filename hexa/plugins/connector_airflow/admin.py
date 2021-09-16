from django.contrib import admin
from .models import (
    Cluster,
    Credentials,
    ClusterPermission,
    DAG,
    DAGConfig,
    DAGRun,
)


@admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = (
        "service_account_email",
        "oidc_target_audience",
    )
    search_fields = ("service_account_email",)


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):

    search_fields = ("name",)


@admin.register(ClusterPermission)
class ClusterPermissionAdmin(admin.ModelAdmin):
    list_display = ("cluster", "team")


@admin.register(DAG)
class DAGAdmin(admin.ModelAdmin):
    pass


@admin.register(DAGConfig)
class DAGConfigAdmin(admin.ModelAdmin):
    pass


@admin.register(DAGRun)
class DAGConfigRunAdmin(admin.ModelAdmin):
    pass
