from django.db.models import QuerySet

from hexa.pipelines.models import PipelineRun
from hexa.user_management.models import Organization, UserInterface
from hexa.workspaces.models import Workspace


class PipelineRunUser(UserInterface):
    def __init__(self, pipeline_run: PipelineRun):
        super().__init__()
        self.pipeline_run: PipelineRun = pipeline_run

    is_active = True
    is_authenticated = True
    is_service_principal = True

    def get_username(self):
        return f"pipeline_{self.pipeline_run.id}"

    def natural_key(self):
        return self.pipeline_run.id

    def has_perm(self, perm, obj=None):
        return False

    def has_feature_flag(self, *args, **kwargs):
        return False

    def accessible_workspaces(self) -> QuerySet:
        return Workspace.objects.filter(id=self.pipeline_run.pipeline.workspace_id)

    def accessible_organizations(self) -> QuerySet:
        return Organization.objects.filter(
            workspaces=self.pipeline_run.pipeline.workspace
        )
