"""Settings for offline agent eval runs.

Inherits the test settings: ephemeral database, dummy storage, no external
hosts. Then re-enables Logfire, which `test.py` disables because gzipped OTLP
requests get captured by `responses` mocks. Eval runs have no such mocks, and
reporting experiments to Logfire is the point.
"""

import os
import re

from .test import *  # noqa: F401, F403

# Must be set before the app registry loads: hexa.assistant.apps reads it in ready().
os.environ["LOGFIRE_SEND_TO_LOGFIRE"] = "true"

# logfire only reads the region out of a token whose body is alphanumeric:
# its pattern ends `[a-zA-Z0-9]+$`. Dataset tokens have a UUID-style body, so
# the match fails and logfire falls back to the US endpoint, where an EU token
# gets a 401. Resolve the region ourselves unless a base URL is already set.
if not os.environ.get("LOGFIRE_BASE_URL"):
    _match = re.match(
        r"^pylf_v\d+_(?P<region>[a-z]{2})_",
        (os.environ.get("LOGFIRE_TOKEN") or "").strip().strip("\"'"),
    )
    if _match:
        os.environ[
            "LOGFIRE_BASE_URL"
        ] = f"https://logfire-{_match['region']}.pydantic.dev"

# Eval spans land in the same Logfire project as production traffic. Without a
# distinct environment they look like real user activity, which would pollute
# the production traces we mine for cases.
os.environ.setdefault("SENTRY_ENVIRONMENT", "eval")
