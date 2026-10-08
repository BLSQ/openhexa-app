"""Phase 0: Analysis of workspace-scoped tokens usage (HEXA-1775).

A workspace token today authenticates the *user*, not the workspace.
Thus, a token issued for workspace A can reach everything its owner can reach.
Before fixing it, we need to know how much traffic would actually break.
This module measures that: it observes token-authenticated GraphQL requests and
records, whether it stayed inside the token's workspace.

``attribution``: which workspace does this object belong to
``classification``: is this request "legal" or not
``extension`` Ariadne extension watcher
"""

from .extension import WorkspaceScopeAudit, audit_extensions

__all__ = ["WorkspaceScopeAudit", "audit_extensions"]
