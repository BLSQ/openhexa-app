"""Workspace metadata copier (runs first; creates the target workspace).

REMOTE branch — ported from ``migrate_lib/workspaces.py``: recreate the
workspace on the target via the ``createWorkspace`` GraphQL mutation, reading
back the server-assigned slug (the server always re-derives the slug from the
name, so we never pass one). The LOCAL (ORM) branch is implemented in a later
phase.
"""

import sys
from typing import Any

from openhexa.graphql.graphql_client.input_types import (
    CountryInput,
    CreateWorkspaceInput,
    UpdateWorkspaceInput,
)

from hexa.workspace_duplicator.endpoints import Endpoint
from hexa.workspace_duplicator.resources.base import ResourceCopier
from hexa.workspace_duplicator.results import DuplicationResult
from hexa.workspace_duplicator.transport import GraphQLError


class WorkspaceMetadataCopier(ResourceCopier):
    name = "workspace"
    label = "Workspace metadata"
    mandatory = True

    def copy(
        self, source: Endpoint, target: Endpoint, result: DuplicationResult
    ) -> None:
        src_ws = self._read_source(source)
        result.workspace_name = src_ws.name

        print("=> Creating target workspace ...")
        if target.is_remote:
            target_slug = self._create_remote(target, src_ws)
        else:
            target_slug = self._create_local(target, src_ws)

        target.slug = target_slug
        result.workspace_slug = target_slug
        print(f"   created with slug '{target_slug}'")
        if source.slug and target_slug != source.slug:
            print(
                f"   note: the server picked its own slug — '{target_slug}' "
                f"instead of source slug '{source.slug}'. The createWorkspace "
                "mutation always derives the slug from the workspace name."
            )

    def _read_source(self, source: Endpoint) -> Any:
        if source.is_remote:
            print(f"=> Fetching source workspace '{source.slug}' ...")
            src_ws = source.client.workspace(slug=source.slug)
            if src_ws is None:
                raise GraphQLError(f"source workspace '{source.slug}' not found")
            print(f"   name: {src_ws.name!r}")
            return src_ws
        return source.workspace

    def _create_remote(self, target: Endpoint, src_ws: Any) -> str:
        """Create the workspace on a remote target, returning the server slug.

        The server (see resolve_create_workspace + create_workspace_slug in
        openhexa-app) ignores any `slug` passed in the input — it derives the
        slug from the name with a random suffix. So we never pass a slug and
        always read the actual slug back from the response.
        """
        countries = [
            CountryInput(code=c.code, alpha3=c.alpha_3, name=c.name, flag=c.flag)
            for c in (src_ws.countries or [])
        ]
        created = target.client.create_workspace(
            input=CreateWorkspaceInput(
                name=src_ws.name,
                description=src_ws.description or "",
                countries=countries,
                load_sample_data=False,
                configuration=src_ws.configuration or {},
                organization_id=target.organization_id,
            )
        )
        if not created.success or created.workspace is None:
            raise GraphQLError(
                "createWorkspace failed: " + ",".join(created.errors or [])
            )
        created_slug = created.workspace.slug

        if src_ws.docker_image:
            upd = target.client.update_workspace(
                input=UpdateWorkspaceInput(
                    slug=created_slug, docker_image=src_ws.docker_image
                )
            )
            if not upd.success:
                print(
                    f"  warning: could not set dockerImage="
                    f"'{src_ws.docker_image}': " + ",".join(upd.errors or []),
                    file=sys.stderr,
                )
        return created_slug

    def _create_local(self, target: Endpoint, src_ws: Any) -> str:
        raise NotImplementedError(
            "LOCAL workspace creation (native ORM clone) is implemented in a "
            "later phase"
        )
