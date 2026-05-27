from hexa.user_management.models import ServicePrincipal, User, UserInterface
from hexa.webapps.models import Webapp


class WebappUser(UserInterface, ServicePrincipal):
    def __init__(self, real_user: User, webapp: Webapp):
        super().__init__()
        self._real_user = real_user
        self.webapp = webapp

    @property
    def real_user(self) -> User:
        return self._real_user

    @property
    def is_active(self):
        return self.real_user.is_active

    @property
    def is_authenticated(self):
        return self.real_user.is_authenticated

    def get_username(self):
        return f"webapp_{self.webapp.id}_as_{self.real_user.id}"

    def has_perm(self, perm, obj=None):
        return self.real_user.has_perm(perm, obj)

    def has_feature_flag(self, *args, **kwargs):
        return self.real_user.has_feature_flag(*args, **kwargs)
