import base64
import json

from hexa.files.api import get_short_lived_downscoped_access_token
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def notebooks_credentials(user: User, workspace: Workspace):
    """
    Provides the notebooks credentials data that allows users to access files
    in the notebooks component.
    """
    bucket_mode = (
        "RO"
        if workspace.workspacemembership_set.filter(
            user=user, role=WorkspaceMembershipRole.VIEWER
        ).exists()
        else "RW"
    )
    token, expires_in = get_short_lived_downscoped_access_token(workspace.bucket_name)
    return {
        "WORKSPACE_BUCKET_NAME": workspace.bucket_name,
        "GCS_TOKEN": token,
        "GCS_BUCKETS": base64.b64encode(
            json.dumps(
                {
                    "buckets": [
                        {
                            "name": workspace.bucket_name,
                            "mode": bucket_mode,
                            "mount": "/workspace",
                        }
                    ]
                }
            ).encode()
        ).decode(),
    }
