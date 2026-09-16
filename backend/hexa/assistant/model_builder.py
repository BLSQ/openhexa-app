"""Turns a model id into a client an organization can run.

Models are named by their pydantic-ai id, "<provider>:<model>", which is all
pydantic-ai needs to pick the right client. We only supply the credentials the id
cannot carry, so reaching for another model is a configuration change rather than
a code one, and reaching for another provider costs one entry in the registry
below.
"""

import logging
from collections.abc import Callable
from decimal import Decimal
from typing import NamedTuple

import genai_prices
from anthropic.lib.vertex import AsyncAnthropicVertex
from django.conf import settings
from pydantic_ai import RunUsage
from pydantic_ai.models import Model as PydanticModel
from pydantic_ai.models import infer_model
from pydantic_ai.providers import Provider, infer_provider_class
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.google_cloud import GoogleCloudProvider

from hexa.assistant.exceptions import AssistantException
from hexa.assistant.models import Conversation
from hexa.user_management.models import AiSettings

logger = logging.getLogger(__name__)

_PROVIDER_SEPARATOR = ":"

_MANAGED_PRICING_PROVIDER = "google-vertex"


class BuiltModel(NamedTuple):
    model: PydanticModel
    api_name: str
    provider_id: str

    def calculate_cost(self, usage: RunUsage) -> Decimal | None:
        """Price `usage`, or None if this model has no known price.

        Agents in one conversation may run on different models, so each prices
        its own usage. `AiModelBuilder.build` prices an empty usage to turn away
        models we cannot meter, so a None here means the price data changed under
        a model we already accepted, and that usage escapes the monthly budget.
        """
        try:
            return genai_prices.calc_price(
                usage, self.api_name, provider_id=self.provider_id
            ).total_price
        except Exception:
            logger.error(
                "cost calculation failed for model=%s provider=%s; "
                "its usage will not count towards any spend limit",
                self.api_name,
                self.provider_id,
            )
            return None


def provider_of(model_id: str) -> str:
    """The provider part of a "<provider>:<model>" id."""
    return model_id.split(_PROVIDER_SEPARATOR, 1)[0]


def is_model_id(value: str) -> bool:
    return _PROVIDER_SEPARATOR in value


def pricing_provider_id(ai_settings: AiSettings, model_id: str) -> str:
    """The provider genai_prices knows this model by.

    It prices managed models by the Google Vertex backend they really run on,
    rather than by the provider that defines them.
    """
    if ai_settings.provider == AiSettings.Provider.MANAGED:
        return _MANAGED_PRICING_PROVIDER
    return provider_of(model_id)


def supports(ai_settings: AiSettings, model_id: str) -> bool:
    """Whether we hold credentials for `model_id`'s provider.

    Managed organizations run on whatever our Vertex project serves, while
    BYOK ones are fixed to the single provider they brought a key for.
    """
    provider = provider_of(model_id)
    if ai_settings.provider == AiSettings.Provider.MANAGED:
        return provider in _managed_providers()
    return provider == ai_settings.provider


def _vertex_anthropic() -> Provider:
    # pydantic-ai has no Anthropic-on-Vertex provider of its own: Claude on
    # Vertex is the Anthropic provider wrapped around Google's client.
    return AnthropicProvider(
        anthropic_client=AsyncAnthropicVertex(
            project_id=settings.VERTEX_PROJECT_ID,
            region=settings.VERTEX_REGION,
        )
    )


def _vertex_google() -> Provider:
    return GoogleCloudProvider(
        project=settings.VERTEX_PROJECT_ID, location=settings.VERTEX_REGION
    )


# What we know how to serve from our own Vertex project. Providers name their
# credentials differently, so each gets an entry rather than one call that
# happens to fit: this registry is what adding a provider costs.
_MANAGED_PROVIDERS: dict[str, Callable[[], Provider]] = {
    "anthropic": _vertex_anthropic,
    "google-cloud": _vertex_google,
}


def _managed_providers() -> dict[str, Callable[[], Provider]]:
    """The entries of the registry this deployment may actually use.

    A publisher has to be enabled on a Vertex project before it answers, which
    staging and production do not agree on, so ASSISTANT_MANAGED_PROVIDERS
    narrows what we know how to build down to what is really there. Empty means
    all of it.
    """
    configured = settings.ASSISTANT_MANAGED_PROVIDERS.replace(" ", "").split(",")
    enabled = set(filter(None, configured)) or set(_MANAGED_PROVIDERS)
    return {p: build for p, build in _MANAGED_PROVIDERS.items() if p in enabled}


def _provider_factory(ai_settings: AiSettings) -> Callable[[str], Provider]:
    """Credentials for whichever provider a model id names.

    Managed organizations run on our own Vertex project;
    everyone else brings the key for the provider they configured.
    """

    def factory(provider: str) -> Provider:
        if not supports(ai_settings, provider):
            raise AssistantException(
                f"Provider {provider!r} cannot run with the credentials of "
                f"{ai_settings.provider!r} organizations"
            )
        if ai_settings.provider != AiSettings.Provider.MANAGED:
            return infer_provider_class(provider)(api_key=ai_settings.api_key)
        if not settings.VERTEX_PROJECT_ID:
            raise AssistantException(
                "VERTEX_PROJECT_ID is not configured; cannot use the managed provider."
            )
        return _managed_providers()[provider]()

    return factory


class AiModelBuilder:
    """Builds the models an organization's AI settings allow.

    It knows how to turn a model id into a usable client, and nothing about who
    wants which model: that decision lives in `model_selection`.
    """

    def __init__(self, ai_settings: AiSettings):
        self._ai_settings = ai_settings

    @classmethod
    def from_conversation(cls, conversation: Conversation) -> "AiModelBuilder":
        organization = conversation.workspace.organization
        if organization is None:
            raise AssistantException(
                "Workspace does not belong to an organization; the assistant is unavailable"
            )
        ai_settings: AiSettings = organization.ai_settings_safe
        if not ai_settings.enabled:
            raise AssistantException("AI settings are not enabled")
        return cls(ai_settings)

    @property
    def ai_settings(self) -> AiSettings:
        return self._ai_settings

    def build(self, model_id: str) -> BuiltModel:
        """Build the "<provider>:<model>" id, with this organization's credentials."""
        try:
            model = infer_model(
                model_id, provider_factory=_provider_factory(self._ai_settings)
            )
        except AssistantException:
            raise
        except Exception as exc:
            # Model ids are free-form configuration: an unknown provider, or one
            # whose optional dependency is not installed, only shows up here.
            raise AssistantException(f"Cannot build model {model_id!r}: {exc}") from exc

        built = BuiltModel(
            model=model,
            api_name=model.model_name,
            provider_id=pricing_provider_id(self._ai_settings, model_id),
        )
        # Usage we cannot price never counts towards the organization's budget,
        # so an unpriceable model would run uncapped. Refuse it while the only
        # thing at stake is a configuration error.
        if built.calculate_cost(RunUsage()) is None:
            raise AssistantException(
                f"No known price for {model_id!r}; refusing to run a model whose "
                f"spend cannot be capped"
            )
        return built
