from django.conf import settings
from django.test import Client
from django_otp import DEVICE_ID_SESSION_KEY

from ..utils import default_device, has_configured_two_factor


class TwoFactorClient(Client):
    def _login(self, user, backend=None):
        super()._login(user, backend)
        if has_configured_two_factor(user):
            device = default_device(user)
            session = self.session
            session[DEVICE_ID_SESSION_KEY] = device.persistent_id
            session.save()
            session_cookie_name = settings.SESSION_COOKIE_NAME
            self.cookies[session_cookie_name] = session.session_key
            cookie_data = {
                "max-age": None,
                "path": "/",
                "domain": settings.SESSION_COOKIE_DOMAIN,
                "secure": settings.SESSION_COOKIE_SECURE or None,
                "expires": None,
            }
            self.cookies[session_cookie_name].update(cookie_data)
