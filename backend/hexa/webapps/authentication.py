"""Principal that represents a request coming from a webapp's GraphQL proxy.

The webapp middleware wraps `request.user` as a `WebappUser` before the schema
runs, so every resolver — `filter_for_user`, `has_perm`, attribution — sees a
principal whose access is already scoped to the webapp's workspace and gated
by the webapp's `allowed_operations`. This is the load-bearing security
boundary for the proxy: defense-in-depth on top of the field-name allowlist.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from hexa.user_management.models import User, UserInterface

if TYPE_CHECKING:
    from hexa.webapps.models import Webapp


class WebappUser(UserInterface):
    """Principal scoped to a single webapp.

    Two flavours, distinguished by whether a human is in the loop:

    - **Private webapp**: `real_user` is the authenticated session user. Access
      is the intersection of what the real user can see and what the webapp's
      workspace is. Writes are attributed to the real user.

    - **Public webapp**: `real_user` is `None`. Access is hard-scoped to the
      webapp's workspace, regardless of session. `has_perm` always denies
      (there's no human to authorize a write), so public webapps are
      effectively read-only at the resolver perm layer.
    """

    is_active = True
    is_authenticated = True
    is_service_principal = True

    def __init__(self, *, webapp: "Webapp", real_user: User | None = None):
        super().__init__()
        self.webapp = webapp
        # A user is only "real" if they are an authenticated User row; anonymous
        # sessions on a private webapp behave the same as a public webapp.
        self.real_user = real_user if isinstance(real_user, User) else None

    def get_username(self):
        if self.real_user is not None:
            return f"webapp_{self.webapp.id}:{self.real_user.get_username()}"
        return f"webapp_{self.webapp.id}"

    def has_perm(self, perm, obj=None):
        """Delegate to the real user and gate by the webapp's allowed_operations.

        Both conditions must hold:
        1. The real user actually has the perm on the object.
        2. The perm maps to a scope the webapp has been granted.

        Perms not registered in `hexa.webapps.scopes.PERM_TO_SCOPE` are denied
        outright — adding a new perm reachable from webapps means registering
        it there first.
        """
        from hexa.webapps.scopes import scope_for_perm

        if self.real_user is None:
            return False
        scope = scope_for_perm(perm)
        if scope is None or scope not in self.webapp.allowed_operations:
            return False
        return self.real_user.has_perm(perm, obj)

    def has_feature_flag(self, *args, **kwargs):
        if self.real_user is None:
            return False
        return self.real_user.has_feature_flag(*args, **kwargs)

    def accessible_workspaces(self):
        from hexa.workspaces.models import Workspace

        scoped = Workspace.objects.filter(pk=self.webapp.workspace_id)
        if self.real_user is None:
            return scoped
        return scoped.filter(pk__in=self.real_user.accessible_workspaces().values("pk"))

    def accessible_organizations(self):
        from hexa.user_management.models import Organization

        org_id = self.webapp.workspace.organization_id
        if org_id is None:
            return Organization.objects.none()
        scoped = Organization.objects.filter(pk=org_id)
        if self.real_user is None:
            return scoped
        return scoped.filter(
            pk__in=self.real_user.accessible_organizations().values("pk")
        )

    @property
    def human_actor(self):
        return self.real_user
