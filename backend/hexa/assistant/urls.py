from django.urls import path

from . import views
from .notebooks import views as notebooks_views

app_name = "assistant"

urlpatterns = [
    path(
        "conversations/<uuid:conversation_id>/stream/",
        views.stream_assistant_message,
        name="stream_assistant_message",
    ),
    # OpenAI-compatible endpoint; the clients append /chat/completions to their
    # base URL, without a trailing slash.
    path(
        "gateway/v1/chat/completions",
        notebooks_views.gateway_chat_completions,
        name="gateway_chat_completions",
    ),
]
