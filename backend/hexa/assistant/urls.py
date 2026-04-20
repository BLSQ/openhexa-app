from django.urls import path

from . import views

app_name = "assistant"

urlpatterns = [
    path(
        "conversations/<uuid:conversation_id>/stream/",
        views.stream_assistant_message,
        name="stream_assistant_message",
    ),
]
