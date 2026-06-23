from hexa.pipelines.models import PipelineRun
from hexa.user_management.models import ServicePrincipal, UserInterface


class PipelineRunUser(UserInterface, ServicePrincipal):
    def __init__(self, pipeline_run: PipelineRun):
        super().__init__()
        self.pipeline_run: PipelineRun = pipeline_run

    is_active = True
    is_authenticated = True

    @property
    def real_user(self):
        # The user who triggered the run, if any (None for scheduled runs).
        return self.pipeline_run.user

    @property
    def workspace(self):
        return self.pipeline_run.pipeline.workspace

    @property
    def workspace_id(self):
        return self.pipeline_run.pipeline.workspace_id

    def get_username(self):
        return f"pipeline_{self.pipeline_run.id}"

    def natural_key(self):
        return self.pipeline_run.id

    def has_perm(self, perm, obj=None):
        return False

    def has_feature_flag(self, *args, **kwargs):
        return False
