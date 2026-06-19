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

from hexa.workspace_duplicator.endpoints import Endpoint
from hexa.workspace_duplicator.resources.base import ResourceCopier
from hexa.workspace_duplicator.results import ConnectionsResult, DuplicationResult
from hexa.workspace_duplicator.transport import GraphQLError, gql

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

    def copy(
        self, source: Endpoint, target: Endpoint, result: DuplicationResult
    ) -> None:
        if source.is_remote and target.is_remote:
            self._copy_remote(source, target, result)
        else:
            raise NotImplementedError(
                "LOCAL connections copy (native ORM clone) is implemented in a "
                "later phase"
            )

    def _copy_remote(
        self, source: Endpoint, target: Endpoint, result: DuplicationResult
    ) -> None:
        conns_result = ConnectionsResult()
        result.connections = conns_result

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
                continue
            try:
                fields_in = _build_fields(conn, conns_result)
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
            except GraphQLError:
                # Collect and continue (like files) so one bad connection
                # doesn't abort the rest of the migration.
                conns_result.failed.append(slug)


def _list_connections(client: Client, slug: str) -> list[dict[str, Any]] | None:
    """Return the workspace's connections, or None if the workspace is absent."""
    data = gql(client, LIST_CONNECTIONS_QUERY, {"slug": slug}, "ListConnections")
    ws = data["workspace"]
    if ws is None:
        return None
    return list(ws["connections"])


def _build_fields(
    conn: dict[str, Any], result: ConnectionsResult
) -> list[ConnectionFieldInput]:
    """Map source fields to ConnectionFieldInput, warning on empty secrets."""
    fields_in: list[ConnectionFieldInput] = []
    for f in conn.get("fields") or []:
        value = f.get("value")
        if f.get("secret") and not value:
            result.warnings.append(
                f"connection '{conn['slug']}' field '{f['code']}' is a secret "
                "with no readable value on source — created empty; set it "
                "manually on the target."
            )
        fields_in.append(
            ConnectionFieldInput(
                code=f["code"], secret=bool(f.get("secret")), value=value
            )
        )
    return fields_in
