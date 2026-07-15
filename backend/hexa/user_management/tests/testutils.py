import uuid
from datetime import timedelta

from django.utils import timezone

from hexa.user_management.models import Organization, OrganizationSubscription


def create_subscription(
    organization: Organization, **overrides
) -> OrganizationSubscription:
    """Create an OrganizationSubscription with sensible defaults for tests.

    Defaults describe an active subscription so callers only need to pass the
    fields their test actually cares about (e.g. an expired ``end_date`` or a
    lower ``users_limit``). New required fields only need a default added here
    rather than in every test that builds a subscription.
    """
    today = timezone.now().date()
    defaults = {
        "subscription_id": uuid.uuid4(),
        "plan_code": "openhexa_starter",
        "start_date": today - timedelta(days=30),
        "end_date": today + timedelta(days=335),
        "users_limit": 10,
        "workspaces_limit": 5,
        "pipeline_runs_limit": 1000,
        "monthly_ai_budget": 50,
    }
    return OrganizationSubscription.objects.create(
        organization=organization, **{**defaults, **overrides}
    )
