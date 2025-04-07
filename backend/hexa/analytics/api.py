from django.conf import settings
from django.http import HttpRequest
from mixpanel import Mixpanel
from sentry_sdk import capture_exception
from ua_parser import user_agent_parser

from hexa.user_management.models import AnonymousUser, User

mixpanel = None
if settings.MIXPANEL_TOKEN:
    from mixpanel_async import AsyncBufferedConsumer

    mixpanel = Mixpanel(
        token=settings.MIXPANEL_TOKEN,
        consumer=AsyncBufferedConsumer(  # See AsyncMixpanelTest for expected behavior
            # It’s a good practice to set connect timeouts to slightly larger than a multiple of 3, which is the default TCP packet retransmission window.
            # https://requests.readthedocs.io/en/latest/user/advanced/#timeouts
            # request_timeout is an int, so using 4 seconds
            request_timeout=4
        ),
    )


def track(
    request: HttpRequest | None,
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
    user: User
       User entity to track
    """
    if mixpanel is None:
        return

    try:
        people = user if user else getattr(request, "user", None)
        can_track = (
            people is None
            or isinstance(people, AnonymousUser)
            or getattr(people, "analytics_enabled", False)
        )
        if can_track is False:
            return

        if request and "User-Agent" in request.headers:
            # Add request related properties
            parsed = user_agent_parser.Parse(request.headers["User-Agent"])
            properties.update(
                {
                    "$browser": parsed["user_agent"]["family"],
                    "$device": parsed["device"]["family"],
                    "$os": parsed["os"]["family"],
                    "ip": request.META["REMOTE_ADDR"],
                }
            )
        mixpanel.track(
            distinct_id=str(people.id) if people else None,
            event_name=event,
            properties=properties,
        )
    except Exception as e:
        capture_exception(e)


def set_user_properties(user: User):
    if mixpanel is None:
        return

    try:
        if getattr(user, "analytics_enabled", False) is False:
            return
        mixpanel.people_set(
            distinct_id=str(user.id),
            properties={
                "$email": user.email,
                "$name": user.display_name,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "features_flag": [f.feature.code for f in user.featureflag_set.all()],
            },
        )
    except Exception as e:
        capture_exception(e)
