from hexa.pipelines.models import PipelineRun
from hexa.user_management.models import UserInterface


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

    def accessible_workspaces(self):
        from hexa.workspaces.models import Workspace

        return Workspace.objects.filter(pk=self.pipeline_run.pipeline.workspace_id)

    def accessible_organizations(self):
        from hexa.user_management.models import Organization

        workspace = self.pipeline_run.pipeline.workspace
        if workspace.organization_id is None:
            return Organization.objects.none()
        return Organization.objects.filter(pk=workspace.organization_id)
