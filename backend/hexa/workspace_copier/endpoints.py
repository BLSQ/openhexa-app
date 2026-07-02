"""Endpoint: a single descriptor for either side of a workspace copy.

Both source and target are ``Endpoint`` values; the read-vs-write asymmetry
lives inside each resource copier (it reads from ``source``, writes to
``target``), not in a Source/Target class hierarchy.

- ``LOCAL`` — same server, operated on via the Django ORM. ``workspace`` holds
  the source ``Workspace`` instance (source) or the created target workspace
  (set by the workspace-metadata copier).
- ``REMOTE`` — another server, reached over GraphQL through ``transport.py``.
  ``client`` is an authenticated SDK ``Client`` and ``slug`` the workspace slug.

``workspace_name`` is a target-only override: when set, the target workspace is
created with this name instead of the source workspace's name.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from openhexa.graphql.graphql_client.client import Client


class EndpointMode(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"


@dataclass
class Endpoint:
    mode: EndpointMode
    slug: str | None = None
    client: Client | None = None
    workspace: Any = None
    organization_id: str | None = None
    workspace_name: str | None = None

    @classmethod
    def local(
        cls,
        slug: str | None = None,
        *,
        workspace: Any = None,
        organization_id: str | None = None,
        workspace_name: str | None = None,
    ) -> Endpoint:
        return cls(
            EndpointMode.LOCAL,
            slug=slug,
            workspace=workspace,
            organization_id=organization_id,
            workspace_name=workspace_name,
        )

    @classmethod
    def remote(
        cls,
        client: Client,
        slug: str | None = None,
        *,
        organization_id: str | None = None,
        workspace_name: str | None = None,
    ) -> Endpoint:
        return cls(
            EndpointMode.REMOTE,
            slug=slug,
            client=client,
            organization_id=organization_id,
            workspace_name=workspace_name,
        )

    @property
    def is_local(self) -> bool:
        return self.mode is EndpointMode.LOCAL

    @property
    def is_remote(self) -> bool:
        return self.mode is EndpointMode.REMOTE
