"""Rules for members duplicating a workspace from the app.

A duplication is a same-server copy run acting as its requester:
``check_can_duplicate`` decides whether they may start one, both when it is
requested and when the worker starts it, and ``issue_requester_token`` then
gives the run a token acting as them.
"""

import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from oauth2_provider.models import AccessToken

from hexa.oauth.scopes import WORKSPACE_COPY_SCOPE
from hexa.user_management.models import User
from hexa.workspace_copier.models import WorkspaceCopyRun
from hexa.workspaces.models import Workspace

REFUSAL_MESSAGES = {
    "WORKSPACE_NOT_FOUND": "The source workspace is no longer available to you.",
    "PERMISSION_DENIED": "You are no longer allowed to duplicate this workspace.",
    "WORKSPACES_LIMIT_REACHED": "The organization has reached its workspace limit.",
}


class DuplicateRefused(Exception):
    """The requester may not (or may no longer) duplicate the source workspace."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(REFUSAL_MESSAGES[code])


class CopyAlreadyRunning(Exception):
    """The requester already has a duplication queued or running."""


def check_can_duplicate(user: User, slug: str, organization_id=None) -> Workspace:
    """Return the workspace ``user`` may duplicate now, or raise DuplicateRefused.

    Checked when the copy is requested and again when it starts, since the
    requester's rights or the organization's plan may change while it waits.
    """
    workspaces = Workspace.objects.filter_for_user(user).filter(slug=slug)
    if organization_id is not None:
        workspaces = workspaces.filter(organization_id=organization_id)
    workspace = workspaces.select_related("organization").first()
    if workspace is None:
        raise DuplicateRefused("WORKSPACE_NOT_FOUND")
    if not user.has_perm("workspaces.duplicate_workspace", workspace):
        raise DuplicateRefused("PERMISSION_DENIED")
    if workspace.organization.is_workspaces_limit_reached():
        raise DuplicateRefused("WORKSPACES_LIMIT_REACHED")
    return workspace


def issue_requester_token(run: WorkspaceCopyRun) -> str:
    """Re-check the requester's rights, then give the run a token acting as them."""
    user = run.created_by
    if user is None or not user.is_active:
        raise DuplicateRefused("PERMISSION_DENIED")
    check_can_duplicate(user, run.source_slug, run.target_organization_id)
    run.access_token = AccessToken.objects.create(
        user=user,
        token=secrets.token_urlsafe(32),
        scope=WORKSPACE_COPY_SCOPE,
        expires=timezone.now()
        + timedelta(seconds=settings.WORKSPACE_COPY_TOKEN_EXPIRE_SECONDS),
    )
    run.save(update_fields=["access_token", "updated_at"])
    return run.access_token.token
