import logging

from django.http.request import HttpRequest
from django.utils import timezone

logger = logging.getLogger(__name__)


def oauth2_token_authentication_middleware(get_response):
    def middleware(request: HttpRequest):
        if request.user.is_authenticated:
            return get_response(request)

        try:
            auth_type, token = request.headers["Authorization"].split(" ")
            if auth_type.lower() == "bearer":
                from oauth2_provider.models import AccessToken

                access_token = AccessToken.objects.select_related("user").get(
                    token=token
                )
                if access_token.expires >= timezone.now():
                    request.user = access_token.user
        except KeyError:
            pass
        except ValueError:
            logger.error("OAuth2 token authentication error")
        except AccessToken.DoesNotExist:
            pass

        return get_response(request)

    return middleware
