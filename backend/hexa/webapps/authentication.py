from hexa.user_management.models import Organization, User, UserInterface
from hexa.webapps.models import Webapp
from hexa.workspaces.models import Workspace


class WebappUser(UserInterface):
    """Service principal a webapp acts as when issuing GraphQL requests
    through the webapp proxy. Wraps the embedding `real_user` so audit /
    permission checks have a fallback, but scopes data access strictly to
    `webapp.workspace` regardless of what the real user can reach.
    """

    is_active = True
    is_authenticated = True
    is_service_principal = True

    def __init__(self, real_user: User, webapp: Webapp):
        super().__init__()
        self.real_user = real_user
        self.webapp = webapp

    def get_username(self):
        return f"webapp_{self.webapp.id}_as_{self.real_user.id}"

    def has_perm(self, perm, obj=None):
        return False

    def has_feature_flag(self, *args, **kwargs):
        return False

    def accessible_workspaces(self):
        return Workspace.objects.filter(id=self.webapp.workspace_id)

    def accessible_organizations(self):
        return Organization.objects.filter(workspaces=self.webapp.workspace)
