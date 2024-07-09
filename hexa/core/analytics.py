from django.conf import settings
from django.http import HttpRequest
from mixpanel import BufferedConsumer, Mixpanel
from sentry_sdk import capture_exception
from ua_parser import user_agent_parser

from hexa.user_management.models import AnonymousUser, User

mixpanel_consumer = BufferedConsumer(max_size=1)
mixpanel = Mixpanel(token=settings.MIXPANEL_TOKEN, consumer=mixpanel_consumer)


def track(
    request: HttpRequest,
    event: str,
    properties: dict = {},
    user: User = None,
):
    """Track event to mixpanel.

    Parameters
    ----------
    request : HttpRequest
    event : str
        An identifier for the event to track.
    properties : dict
       A dictionary holding the event properties
    user: User |
       User entity to track
    """
    if settings.MIXPANEL_TOKEN:
        # First check if we have a PipelineUser and get the associated user if it exits
        # user will be None in case of pipeline triggered via schedule or webhook
        if request:
            parsed = user_agent_parser.Parse(request.headers["User-Agent"])
            properties.update(
                {
                    "$browser": parsed["user_agent"]["family"],
                    "$device": parsed["device"]["family"],
                    "$os": parsed["os"]["family"],
                    "ip": request.META["REMOTE_ADDR"],
                }
            )

        can_track = (
            user is None or isinstance(user, AnonymousUser) or user.analytics_enabled
        )
        if can_track:
            try:
                mixpanel.track(
                    distinct_id=str(user.id) if user else None,
                    event_name=event,
                    properties=properties,
                )
            except Exception as e:
                print(e, flush=True)
                capture_exception(e)


def set_user_properties(user: User):
    if settings.MIXPANEL_TOKEN and user.analytics_enabled:
        try:
            mixpanel.people_set_once(
                distinct_id=str(user.id),
                properties={
                    "$email": user.email,
                    "$name": user.display_name,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "email_domain": user.email.split("@")[1],
                    "features_flag": [
                        f.feature.code for f in user.featureflag_set.all()
                    ],
                },
            )
        except Exception as e:
            capture_exception(e)
