"""Seeded workspaces the agents are evaluated against.

A profile decides what `list_connections`, `list_datasets` and `list_files`
return to the agent, and it is what the grounding verifier checks invented
identifiers against.

Profiles are shared across suites.
"""

from __future__ import annotations

import io
import uuid
from collections.abc import Callable
from dataclasses import dataclass

from django.conf import settings
from django.db import connection as db_connection

from hexa.datasets.models import Dataset
from hexa.files import storage
from hexa.user_management.models import Organization, User
from hexa.workspaces.models import (
    Connection,
    ConnectionField,
    ConnectionType,
    Workspace,
)
from hexa.workspaces.tests.testutils import create_workspace

from .verifiers import WorldSpec

STANDARD_WORKSPACE = "standard_workspace"

_STANDARD_CONNECTIONS: dict[
    str, tuple[str, ConnectionType, dict[str, tuple[str, bool]]]
] = {
    "dhis2-play": ("DHIS2 Play", ConnectionType.DHIS2, {}),
    "dhis2-target": ("DHIS2 Target", ConnectionType.DHIS2, {}),
    "iaso-staging": ("IASO Staging", ConnectionType.IASO, {}),
    "cds-climate": (
        "CDS Climate",
        ConnectionType.CUSTOM,
        {"url": ("https://cds.climate.example/api", False), "key": ("eval-key", True)},
    ),
}

_STANDARD_DATASETS = {
    "boundaries": (
        "Boundaries",
        "Administrative boundaries used by the climate pipelines.",
    ),
    "analytics-output": ("Analytics Output", "Target dataset for extracted analytics."),
}

_STANDARD_FILES = {
    "data/mapping.csv": b"source_de,target_de\nabc123,def456\n",
    "data/boundaries/district.parquet": b"PAR1",
    "data/raw/facilities.csv": b"id,name\n1,Clinic\n",
}


SPECS: dict[str, WorldSpec] = {
    STANDARD_WORKSPACE: WorldSpec(
        connection_slugs=frozenset(_STANDARD_CONNECTIONS),
        dataset_slugs=frozenset(_STANDARD_DATASETS),
        file_paths=frozenset(_STANDARD_FILES),
    ),
}


def profile_spec(name: str) -> WorldSpec:
    """The world a case is graded against, without building it."""
    if name not in SPECS:
        raise KeyError(
            f"Unknown fixture_profile {name!r}. Known profiles: {', '.join(sorted(SPECS))}."
        )
    return SPECS[name]


class UnsafeDatabaseError(RuntimeError):
    """Raised when a fixture would be built outside an ephemeral test database."""


@dataclass(frozen=True)
class EvalWorld:
    """A built profile: the Django objects plus the verifiers' view of them."""

    user: User
    workspace: Workspace
    spec: WorldSpec


def assert_ephemeral_database() -> None:
    """Refuse to seed fixtures into anything but a throwaway database.

    Django names test databases `test_<name>`. Any other name means the settings
    module is wrong and the run would write to real data.
    """
    name = db_connection.settings_dict.get("NAME") or ""
    if not name.startswith("test_"):
        raise UnsafeDatabaseError(
            f"Refusing to build eval fixtures against database {name!r}: "
            "eval runs require an ephemeral test database."
        )


def _new_workspace(user: User, name: str) -> Workspace:
    """Create a workspace under an organization named uniquely for this build.

    Every repeat of every case builds its own world, so the default helper's
    `"<workspace name> Organization"` would collide on Organization.name after
    the first build.
    """
    organization = Organization.objects.create(
        name=f"{name} Organization {uuid.uuid4().hex[:8]}"
    )
    return create_workspace(user, name=name, organization=organization)


def _seed_file(workspace: Workspace, path: str, content: bytes) -> None:
    if not storage.bucket_exists(workspace.bucket_name):
        storage.create_bucket(workspace.bucket_name)
    storage.save_object(workspace.bucket_name, path, io.BytesIO(content))


def _add_connection(
    user: User,
    workspace: Workspace,
    *,
    name: str,
    slug: str,
    connection_type: ConnectionType,
    fields: dict[str, tuple[str, bool]],
) -> Connection:
    connection = Connection.objects.create_if_has_perm(
        user,
        workspace=workspace,
        name=name,
        slug=slug,
        connection_type=connection_type,
    )
    for code, (value, secret) in fields.items():
        ConnectionField.objects.create(
            connection=connection, user=user, code=code, value=value, secret=secret
        )
    return connection


def _instance_fields(url: str) -> dict[str, tuple[str, bool]]:
    return {
        "url": (url, False),
        "username": ("eval", False),
        "password": ("eval-password", True),
    }


def build_standard_workspace(user: User) -> EvalWorld:
    """A workspace stocked with everything the create-suite cases refer to.

    Two DHIS2 connections because the dhis2-to-dhis2 task needs a source and a
    target; the rest covers the connection types the templates exercise.
    """
    workspace = _new_workspace(user, "Eval Standard Workspace")

    for slug, (name, connection_type, extra_fields) in _STANDARD_CONNECTIONS.items():
        fields = extra_fields or _instance_fields(f"https://{slug}.example/eval")
        _add_connection(
            user,
            workspace,
            name=name,
            slug=slug,
            connection_type=connection_type,
            fields=fields,
        )

    for name, description in _STANDARD_DATASETS.values():
        Dataset.objects.create_if_has_perm(
            user, workspace=workspace, name=name, description=description
        )

    for path, content in _STANDARD_FILES.items():
        _seed_file(workspace, path, content)

    return EvalWorld(user=user, workspace=workspace, spec=SPECS[STANDARD_WORKSPACE])


# One profile today, but kept as a registry: `fixture_profile` is stored in
# every hosted case, so adding a world means adding an entry here and pointing
# cases at it, with no change to the runner.
PROFILES: dict[str, Callable[[User], EvalWorld]] = {
    STANDARD_WORKSPACE: build_standard_workspace,
}


def build_profile(name: str, user: User) -> EvalWorld:
    """Build a named profile, failing loudly on an unknown name.

    Called during startup validation so a case pointing at a profile that does
    not exist fails before any model tokens are spent.
    """
    assert_ephemeral_database()
    profile_spec(name)
    if not storage.bucket_exists(settings.WORKSPACE_DATASETS_BUCKET):
        storage.create_bucket(settings.WORKSPACE_DATASETS_BUCKET)
    return PROFILES[name](user)
