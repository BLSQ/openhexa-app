from datetime import datetime

from django.conf import settings
from django.http import HttpRequest
from mixpanel import BufferedConsumer, Mixpanel
from sentry_sdk import capture_exception
from ua_parser import user_agent_parser

mixpanel_consumer = BufferedConsumer()


def track(
    user,
    event: str,
    properties: dict = {},
    request: HttpRequest = None,
):
    """Track event to mixpanel.
    Parameters request.user.pipeline_run.pipeline.workspace
    ----------
    user : any
        The user that initiated the even
    event : str
        An identifier for the event to track.
    properties : dict
       A dictionary holding the event properties
     request : HttpRequest | None
    """
    from hexa.pipelines.authentication import PipelineRunUser

    if not settings.MIXPANEL_TOKEN:
        return

    # First check if we have a PipelineUser and get the associated user if it exits
    # user will be None in case of pipeline triggered via schedule or webhook
    tracked_user = user
    if isinstance(user, PipelineRunUser):
        tracked_user = user.pipeline_run.user

    if tracked_user is None or tracked_user.analytics_enabled:
        try:
            mixpanel = Mixpanel(
                token=settings.MIXPANEL_TOKEN, consumer=mixpanel_consumer
            )
            # for request coming from openHEXA pipelines we don't need to store those info
            if not isinstance(user, PipelineRunUser) and request:
                parsed = user_agent_parser.Parse(request.headers["User-Agent"])
                properties.update(
                    {
                        "$browser": parsed["user_agent"]["family"],
                        "$device": parsed["device"]["family"],
                        "$os": parsed["os"]["family"],
                        "ip": request.META["REMOTE_ADDR"],
                    }
                )
            properties.update(
                {
                    "timestamp": datetime.now().timestamp(),
                    # "app_version": APP_VERSION
                }
            )

            id = str(tracked_user.id) if tracked_user else None
            mixpanel.track(
                distinct_id=id,
                event_name=event,
                properties=properties,
            )
            if tracked_user:
                # create user profile on
                mixpanel.people_set_once(
                    distinct_id=id,
                    properties={
                        "$email": tracked_user.email,
                        "$name": tracked_user.display_name,
                        "staff_status": tracked_user.is_staff,
                        "superuser_status": tracked_user.is_superuser,
                        "email_domain": tracked_user.email.split("@")[1],
                        "features_flag": [
                            f.feature.code for f in tracked_user.featureflag_set.all()
                        ],
                    },
                )

        except Exception as e:
            capture_exception(e)
