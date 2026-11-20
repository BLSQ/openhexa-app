from hexa.user_management.models import User

from .models import WorkspaceCopyRun


def view_workspace_copy_run(principal: User, run: WorkspaceCopyRun):
    """A run's logs name the requester's resources, so only they can follow it."""
    return run.created_by_id is not None and run.created_by_id == principal.id
