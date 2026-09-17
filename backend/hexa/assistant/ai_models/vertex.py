"""How we reach the models on our own Vertex server.

Vertex speaks a different API per publisher — Gemini through google-genai, Claude
through Anthropic's own client, everything else through an OpenAI-compatible
endpoint — and each names its credentials differently.
"""

from collections.abc import Callable
from functools import cache

import google.auth
from anthropic.lib.vertex import AsyncAnthropicVertex
from django.conf import settings
from google.auth.transport.requests import Request as GoogleAuthRequest
from pydantic_ai.providers import Provider
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.google_cloud import GoogleCloudProvider
from pydantic_ai.providers.openai import OpenAIProvider


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


@cache
def _google_credentials():
    """Our service account, read once and refreshed in place as it expires."""
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    return credentials


def _vertex_openai() -> Provider:
    """Vertex's OpenAI-compatible endpoint, which serves every Model Garden
    publisher that is neither Gemini nor Claude: Qwen, Kimi, DeepSeek, Llama, gpt-oss.
    Example: "openai-chat:qwen/qwen3-coder-480b-a35b-instruct-maas"

    It authenticates with a bearer token rather than a key,
    which is why it builds its own client
    """
    credentials = _google_credentials()
    if not credentials.valid:
        credentials.refresh(GoogleAuthRequest())
    region = settings.VERTEX_MAAS_REGION
    host = (
        "aiplatform.googleapis.com"
        if region == "global"
        else f"{region}-aiplatform.googleapis.com"
    )
    return OpenAIProvider(
        base_url=(
            f"https://{host}/v1/projects/{settings.VERTEX_PROJECT_ID}"
            f"/locations/{region}/endpoints/openapi"
        ),
        api_key=credentials.token,
    )


PROVIDERS: dict[str, Callable[[], Provider]] = {
    "anthropic": _vertex_anthropic,
    "google-cloud": _vertex_google,
    "openai-chat": _vertex_openai,
}
