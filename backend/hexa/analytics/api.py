from django.conf import settings
from django.http import HttpRequest
from mixpanel import Mixpanel
from sentry_sdk import capture_exception
from ua_parser import user_agent_parser

from hexa.user_management.models import AnonymousUser, Feature, Organization, User
from hexa.workspaces.models import Workspace, WorkspaceMembership

mixpanel = None
if settings.MIXPANEL_TOKEN:
    from mixpanel_async import AsyncBufferedConsumer

    mixpanel = Mixpanel(
        token=settings.MIXPANEL_TOKEN,
        consumer=AsyncBufferedConsumer(  # See AsyncMixpanelTest for expected behavior
            # It’s a good practice to set connect timeouts to slightly larger than a multiple of 3, which is the default TCP packet retransmission window.
            # https://requests.readthedocs.io/en/latest/user/advanced/#timeouts
            # request_timeout is an int, so using 4 seconds
            request_timeout=4,
            api_host=settings.MIXPANEL_API_HOST,
        ),
    )


def _resolve_workspace_organization(workspace_slug: str) -> str | None:
    return (
        Workspace.objects.filter(slug=workspace_slug)
        .values_list("organization__name", flat=True)
        .first()
    )


def track(
    request: HttpRequest | None,
    event: str,
    properties: dict | None = None,
    user: User | None = None,
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

        event_properties = dict(properties) if properties else {}
        workspace_slug = event_properties.get("workspace")
        if (
            isinstance(workspace_slug, str)
            and workspace_slug
            and "organization" not in event_properties
        ):
            org_name = _resolve_workspace_organization(workspace_slug)
            if org_name:
                event_properties["organization"] = org_name

        if request and "User-Agent" in request.headers:
            parsed = user_agent_parser.Parse(request.headers["User-Agent"])
            event_properties.update(
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
            properties=event_properties,
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
                "$created": user.date_joined.isoformat() if user.date_joined else None,
                "language": user.language,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "features_flag": list(
                    Feature.objects.are_enabled_for_user(user=user).values_list(
                        "code", flat=True
                    )
                ),
                "organizations": list(
                    Organization.objects.filter(organizationmembership__user=user)
                    .order_by("name")
                    .values_list("name", flat=True)
                    .distinct()
                ),
                "workspace_count": WorkspaceMembership.objects.filter(
                    user=user, workspace__archived=False
                ).count(),
            },
        )
    except Exception as e:
        capture_exception(e)
