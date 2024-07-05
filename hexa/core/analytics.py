from datetime import datetime
from uuid import uuid4

from django.http import HttpRequest
from mixpanel import BufferedConsumer, Mixpanel, MixpanelException
from sentry_sdk import capture_exception
from ua_parser import user_agent_parser

from config.settings.base import MIX_PANEL_BUFFER_SIZE, MIX_PANEL_TOKEN

mixpanel_consumer = BufferedConsumer(max_size=MIX_PANEL_BUFFER_SIZE)
mixpanel = Mixpanel(token=MIX_PANEL_TOKEN, consumer=mixpanel_consumer)


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

    if user is None:
        id = uuid4()
        mixpanel.track(distinct_id=str(id), event_name=event, properties=properties)

    _user = user
    if isinstance(user, PipelineRunUser):
        _user = user.pipeline_run.user

    if _user.analytics_enabled:
        try:
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

            id = _user.id if _user else uuid4()
            mixpanel.track(distinct_id=str(id), event_name=event, properties=properties)
        except MixpanelException as e:
            capture_exception(e)
