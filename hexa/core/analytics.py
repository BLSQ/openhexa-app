from django.conf import settings
from django.http import HttpRequest
from mixpanel import BufferedConsumer, Mixpanel
from sentry_sdk import capture_exception
from ua_parser import user_agent_parser

from hexa.user_management.models import User

mixpanel_consumer = BufferedConsumer()


def track(
    request: HttpRequest,
    event: str,
    properties: dict = {},
):
    """Track event to mixpanel.

    Parameters
    ----------
    request : HttpRequest
    event : str
        An identifier for the event to track.
    properties : dict
       A dictionary holding the event properties
    """
    from hexa.pipelines.authentication import PipelineRunUser

    mixpanel = None
    if settings.MIXPANEL_TOKEN:
        mixpanel = Mixpanel(token=settings.MIXPANEL_TOKEN, consumer=mixpanel_consumer)

    # First check if we have a PipelineUser and get the associated user if it exits
    # user will be None in case of pipeline triggered via schedule or webhook
    tracked_user = None
    if request:
        tracked_user = (
            request.user.pipeline_run.user
            if isinstance(request.user, PipelineRunUser)
            else request.user
        )

        parsed = user_agent_parser.Parse(request.headers["User-Agent"])
        properties.update(
            {
                "$browser": parsed["user_agent"]["family"],
                "$device": parsed["device"]["family"],
                "$os": parsed["os"]["family"],
                "ip": request.META["REMOTE_ADDR"],
            }
        )

    if tracked_user is None or tracked_user.analytics_enabled:
        try:
            mixpanel.track(
                distinct_id=str(tracked_user.id) if tracked_user else None,
                event_name=event,
                properties=properties,
            )
        except Exception as e:
            capture_exception(e)


def track_user(user: User):
    if settings.MIXPANEL_TOKEN and user.analytics_enabled:
        try:
            mixpanel = Mixpanel(
                token=settings.MIXPANEL_TOKEN, consumer=mixpanel_consumer
            )
            mixpanel.people_set_once(
                distinct_id=str(user.id),
                properties={
                    "$email": user.email,
                    "$name": user.display_name,
                    "staff_status": user.is_staff,
                    "superuser_status": user.is_superuser,
                    "email_domain": user.email.split("@")[1],
                    "features_flag": [
                        f.feature.code for f in user.featureflag_set.all()
                    ],
                },
            )
        except Exception as e:
            capture_exception(e)
