"""Connection copier: copy every workspace connection to the target.

REMOTE branch — ported from ``migrate_lib/connections.py``. Secret field values
come through the source API only because we authenticate as a Django superuser:
the ``value`` resolver redacts secret fields unless the caller has
``workspaces.update_connection``, which a superuser short-circuits to True. If a
secret still comes back empty, the connection is created anyway and a warning is
recorded — the user must set that secret manually on the target.

Connection slugs are preserved: unlike createWorkspace / createPipeline (which
re-derive the slug/code server-side), createConnection honors a caller-supplied
slug and only suffixes it on collision. The target workspace is fresh, so the
source slug carries over intact, keeping pipeline parameters that reference a
connection by slug valid.

The LOCAL (ORM) branch is implemented in a later phase.
"""

from typing import Any

from openhexa.graphql.graphql_client.client import Client
from openhexa.graphql.graphql_client.input_types import (
    ConnectionFieldInput,
    ConnectionType,
    CreateConnectionInput,
)

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.options import CopyOptions
from hexa.workspace_copier.progress import ProgressReporter
from hexa.workspace_copier.resources.base import ResourceCopier
from hexa.workspace_copier.results import ConnectionsResult, CopyResult
from hexa.workspace_copier.transport import GraphQLError, gql

# `workspace.connections` is a (non-paginated) field on Workspace returning the
# full list; the SDK's workspace() doesn't pull fields, so we query it raw.
LIST_CONNECTIONS_QUERY = """
query ListConnections($slug: String!) {
    workspace(slug: $slug) {
        connections {
            id name slug description type
            fields { code value secret }
        }
    }
}
"""


class ConnectionsCopier(ResourceCopier):
    name = "connections"
    label = "Connections"
    option_fields = ("include_connection_secrets",)

    def copy(
        self,
        source: Endpoint,
        target: Endpoint,
        result: CopyResult,
        reporter: ProgressReporter,
        *,
        options: CopyOptions = CopyOptions(),
    ) -> None:
        if source.is_remote and target.is_remote:
            self._copy_remote(source, target, result, reporter, options)
        else:
            raise NotImplementedError(
                "LOCAL connections copy (native ORM clone) is implemented in a "
                "later phase"
            )

    def _copy_remote(
        self,
        source: Endpoint,
        target: Endpoint,
        result: CopyResult,
        reporter: ProgressReporter,
        options: CopyOptions,
    ) -> None:
        conns_result = ConnectionsResult()
        result.connections = conns_result
        include_secrets = options.include_connection_secrets
        if not include_secrets:
            conns_result.warnings.append(
                "secrets were not copied — secret fields were created empty; "
                "set them manually on the target."
            )

        conns = _list_connections(source.client, source.slug)
        if conns is None:
            raise GraphQLError(
                f"source workspace '{source.slug}' not found while listing connections"
            )

        existing = {
            c["slug"] for c in (_list_connections(target.client, target.slug) or [])
        }

        for conn in conns:
            slug = conn["slug"]
            if slug in existing:
                conns_result.skipped.append(slug)
                reporter.info(f"   skipped connection '{slug}' (already exists)")
                continue
            try:
                fields_in = _build_fields(conn, conns_result, include_secrets)
                res = target.client.create_connection(
                    input=CreateConnectionInput(
                        workspace_slug=target.slug,
                        name=conn["name"],
                        slug=slug,
                        type=ConnectionType(conn["type"]),
                        description=conn.get("description") or "",
                        fields=fields_in,
                    )
                )
                if not res.success or res.connection is None:
                    raise GraphQLError(
                        f"createConnection failed for '{slug}': "
                        + ",".join(e.value for e in (res.errors or []))
                    )
                conns_result.created.append((slug, len(fields_in)))
                reporter.info(f"   created connection '{slug}'")
            except GraphQLError:
                # Collect and continue (like files) so one bad connection
                # doesn't abort the rest of the copy.
                conns_result.failed.append(slug)
                reporter.warning(f"   FAILED to create connection '{slug}'")


def _list_connections(client: Client, slug: str) -> list[dict[str, Any]] | None:
    """Return the workspace's connections, or None if the workspace is absent."""
    data = gql(client, LIST_CONNECTIONS_QUERY, {"slug": slug}, "ListConnections")
    ws = data["workspace"]
    if ws is None:
        return None
    return list(ws["connections"])


def _build_fields(
    conn: dict[str, Any], result: ConnectionsResult, include_secrets: bool
) -> list[ConnectionFieldInput]:
    """Map source fields to ConnectionFieldInput, blanking secrets unless included.

    An empty secret is only warned about when secrets were requested: when they
    were deliberately skipped, the run-wide warning already covers it.
    """
    fields_in: list[ConnectionFieldInput] = []
    for f in conn.get("fields") or []:
        secret = bool(f.get("secret"))
        value = f.get("value") if include_secrets or not secret else None
        if secret and include_secrets and not value:
            result.warnings.append(
                f"connection '{conn['slug']}' field '{f['code']}' is a secret "
                "with no readable value on source — created empty; set it "
                "manually on the target."
            )
        fields_in.append(
            ConnectionFieldInput(code=f["code"], secret=secret, value=value)
        )
    return fields_in
