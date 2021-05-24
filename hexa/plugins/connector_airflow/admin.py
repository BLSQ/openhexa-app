from django.contrib import admin
from .models import (
    Cluster,
    Credentials,
    ClusterPermission,
    DAG,
    DAGConfig,
    DAGConfigRun,
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
    list_display = (
        "name",
        "airflow_web_url",
    )
    search_fields = ("name",)


@admin.register(ClusterPermission)
class ClusterPermissionAdmin(admin.ModelAdmin):
    list_display = ("cluster", "team")


@admin.register(DAG)
class DAGAdmin(admin.ModelAdmin):
    list_display = (
        "cluster",
        "airflow_id",
    )
    search_fields = ("airflow_id",)


@admin.register(DAGConfig)
class DAGConfigAdmin(admin.ModelAdmin):
    list_display = (
        "dag",
        "name",
    )
    search_fields = ("name",)


@admin.register(DAGConfigRun)
class DAGConfigRunAdmin(admin.ModelAdmin):
    list_display = (
        "airflow_run_id",
        "airflow_state",
        "airflow_execution_date",
    )
    search_fields = ("run_id",)
