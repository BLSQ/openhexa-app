"""Endpoint: a single descriptor for either side of a workspace copy.

Both source and target are ``Endpoint`` values; the read-vs-write asymmetry
lives inside each resource copier (it reads from ``source``, writes to
``target``), not in a Source/Target class hierarchy.

Both sides are reached over GraphQL through ``transport.py``, this server
included. ``client`` is an authenticated SDK ``Client`` and ``slug`` the
workspace slug; ``workspace`` caches whatever :meth:`Endpoint.get_workspace`
last read.

``workspace_name`` is a target-only override: when set, the target workspace is
created with this name instead of the source workspace's name.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openhexa.graphql.graphql_client.client import Client

from hexa.workspace_copier.transport import GraphQLError


@dataclass
class Endpoint:
    client: Client
    slug: str | None = None
    workspace: Any = None
    organization_id: str | None = None
    workspace_name: str | None = None

    def get_workspace(self, side: str) -> Any:
        """Return this endpoint's workspace, reading it at most once.

        The result is cached on ``workspace``, so a slug already resolved during
        pre-flight (the ``--target-workspace-slug`` flow, which stores what it
        verified) costs no second round trip. ``side`` only labels the error.
        """
        if self.workspace is None:
            ws = self.client.workspace(slug=self.slug)
            if ws is None:
                raise GraphQLError(f"{side} workspace '{self.slug}' not found")
            self.workspace = ws
        return self.workspace
