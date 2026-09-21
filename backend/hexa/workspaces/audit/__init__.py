"""Phase 0 analysis for workspace-scoped tokens (HEXA-1775).

A workspace token today authenticates the *user*, not the workspace, so a
token issued for workspace A can reach everything its owner can reach. Before
changing that we need to know how much traffic would actually break, which is
what this measures: it observes token-authenticated GraphQL requests and
records, for each one, whether it stayed inside the token's workspace.

Developed as an Ariadne extension, it only watches objects flow past.
It deliberately doesn't interact with them, it just saves what happens for
visualization and information.

``attribution`` answers "which workspace does this object belong to",
``classification`` answers "is reaching that workspace legitimate", and
``extension`` is the Ariadne adapter that drives both across a request.
"""

from .extension import WorkspaceScopeAudit, audit_extensions

__all__ = ["WorkspaceScopeAudit", "audit_extensions"]
