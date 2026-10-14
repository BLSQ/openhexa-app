"""Settings for offline agent eval runs.

Inherits the test settings: ephemeral database, dummy storage, no external
hosts. Then re-enables Logfire, which `test.py` disables because gzipped OTLP
requests get captured by `responses` mocks. Eval runs have no such mocks, and
reporting experiments to Logfire is the point.
"""

import os
import re
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from .test import *  # noqa: F401, F403

# Must be set before the app registry loads: hexa.assistant.apps reads it in ready().
os.environ["LOGFIRE_SEND_TO_LOGFIRE"] = "true"

# Without credentials, logfire.configure() fails during app startup with "You
# are not logged into Logfire", which never mentions the token. Fail here
# instead, with a message that does. A `logfire auth` credentials file in
# .logfire/ is logfire's other supported setup, so it counts too.
_token = (os.environ.get("LOGFIRE_TOKEN") or "").strip().strip("\"'")
if not _token and not Path(".logfire/logfire_credentials.json").exists():
    raise ImproperlyConfigured(
        "LOGFIRE_TOKEN is not set. Eval runs report each experiment to Logfire, "
        "so they need a token with write access to the project. See .env.dist."
    )

# logfire only reads the region out of a token whose body is alphanumeric: its
# pattern ends `[a-zA-Z0-9]+$`. API keys (`pylf_v2_…`) have a UUID-style body, so
# the match fails and spans go to the US endpoint, where an EU key gets a 401.
# Resolve the region ourselves unless a base URL is already set.
if not os.environ.get("LOGFIRE_BASE_URL"):
    _match = re.match(r"^pylf_v\d+_(?P<region>[a-z]{2})_", _token)
    if _match:
        os.environ[
            "LOGFIRE_BASE_URL"
        ] = f"https://logfire-{_match['region']}.pydantic.dev"

# Eval spans land in the same Logfire project as production traffic. Without a
# distinct environment they look like real user activity, which would pollute
# the production traces we mine for cases.
os.environ.setdefault("SENTRY_ENVIRONMENT", "eval")
