"""
WSGI config for hexa.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import re

from a2wsgi import ASGIMiddleware
from django.core.asgi import get_asgi_application
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

_wsgi_app = get_wsgi_application()
_asgi_app = ASGIMiddleware(get_asgi_application())

# Only the SSE streaming endpoint needs async — route it through ASGI,
# everything else stays on the standard sync WSGI path.
_SSE_PATH_RE = re.compile(r"^/pipelines/runs/[^/]+/messages/stream/")


def application(environ, start_response):
    if _SSE_PATH_RE.match(environ.get("PATH_INFO", "")):
        return _asgi_app(environ, start_response)
    return _wsgi_app(environ, start_response)
