from uuid import uuid4

from mixpanel import Mixpanel, MixpanelException
from sentry_sdk import capture_exception

from config.settings.base import MIX_PANEL_TOKEN


def get_mix_panel_client():
    return Mixpanel(MIX_PANEL_TOKEN)


def create_event(event: str, properties: dict):
    """Send event using mixpanel a Python function as an OpenHEXA pipeline.

    Parameters
    ----------
    event : str
        An identifier for the event to track.
    properties : dict
       A dictionary holding the event details
    """
    try:
        print(f"Event - {event} - Properties {properties}", flush=True)
        mix_panel = get_mix_panel_client()
        mix_panel.track(
            distinct_id=str(uuid4()), event_name=event, properties=properties
        )
    except MixpanelException as e:
        capture_exception(e)
