"""End-to-end harness for the workspace copier.

Runs the *real* copy flow in-process against the real OpenHEXA server code: a
test seeds a genuine source workspace via the ORM, then calls
``service.run_copy`` with SDK clients whose HTTP transport is an
``httpx.WSGITransport`` routed at the in-process Django app. Every GraphQL
request therefore goes through the full stack — middleware (including
ServiceAccount Bearer auth), resolvers, permission filtering and the test
database — with no sockets and no second server.

Source and target are the same in-process app reached with two different
ServiceAccount tokens, which faithfully exercises the copier's remote→remote
branches (the only implemented ones). See ``E2E_TEST_PLAN.md`` for the rationale
and its one limitation (both "servers" run the same schema version).
"""

import io
import tempfile
import zipfile
from unittest.mock import patch

import httpx
from django.core.signals import request_finished, request_started
from django.core.wsgi import get_wsgi_application
from django.db import close_old_connections
from django.test import override_settings

from hexa.core.test import GraphQLTestCase
from hexa.countries.models import Country
from hexa.files import storage
from hexa.files.backends.fs import FileSystemStorage
from hexa.pipelines.models import Pipeline, PipelineType, PipelineVersion
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    ServiceAccount,
)
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.service import run_copy
from hexa.workspaces.models import (
    Connection,
    ConnectionType,
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)

TESTSERVER = "http://testserver"
GRAPHQL_URL = f"{TESTSERVER}/graphql/"

# Built once: a WSGI handler is cheap to reuse and thread-safe for the
# synchronous, single-threaded calls httpx.WSGITransport makes.
_WSGI_APP = get_wsgi_application()


def wsgi_client_factory() -> httpx.Client:
    """A fresh SDK-ready client whose transport is the in-process Django app.

    Fresh each call because ``build_client`` mutates the client it is handed
    (sets the ``Authorization`` header), and source and target use different
    tokens. The files copier reuses this same factory for presigned traffic; it
    relies on the client being *bare* here (no auth header) so presigned URLs,
    which are self-authenticating, are not rejected — see resources/files.py.
    """
    return httpx.Client(
        transport=httpx.WSGITransport(app=_WSGI_APP),
        base_url=TESTSERVER,
        timeout=httpx.Timeout(300.0),
    )


def _make_zipfile(marker: bytes = b"pipeline") -> bytes:
    """A real (openable) zip so any server-side ZipFile read succeeds.

    Versions are always seeded with explicit parameters, so the server never
    parses this zip for parameters; it is still a genuine archive so nothing
    downstream chokes on it.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("pipeline.py", marker)
    return buf.getvalue()


@override_settings(BASE_URL=TESTSERVER, WORKSPACE_BUCKET_PREFIX="")
class WorkspaceCopierE2ETestCase(GraphQLTestCase):
    """Base case: in-process WSGI clients, fs storage, real server code.

    Seeding happens in ``setUp`` (not ``setUpTestData``) because the source
    bucket and its files must land in the *per-test* filesystem storage, which
    only exists after the storage swap below.
    """

    def setUp(self):
        super().setUp()

        # The real WSGI handler fires request_started/request_finished, whose
        # default receiver (close_old_connections) would close the test's
        # transaction-wrapped DB connection after the very first in-process
        # request. Django's own test client disconnects that receiver for the
        # same reason; we do it here for the duration of the test.
        request_started.disconnect(close_old_connections)
        request_finished.disconnect(close_old_connections)
        self.addCleanup(lambda: request_started.connect(close_old_connections))
        self.addCleanup(lambda: request_finished.connect(close_old_connections))

        # True externals: real Postgres role/DB creation needs a superuser and
        # leaks state, so it is patched out exactly as the workspaces schema
        # tests do. Nothing else is patched — the whole copy is real.
        for target in (
            "hexa.workspaces.models.create_database",
            "hexa.workspaces.models.load_database_sample_data",
        ):
            patcher = patch(target)
            patcher.start()
            self.addCleanup(patcher.stop)

        self._swap_in_filesystem_storage()

        self.source_org = Organization.objects.create(name="Source Org")
        self.target_org = Organization.objects.create(name="Target Org")

    def _swap_in_filesystem_storage(self):
        """Point the lazy ``storage`` proxy at a real per-test filesystem backend.

        ``hexa.files.storage`` is a module-level ``SimpleLazyObject`` imported by
        reference everywhere, so ``override_settings(WORKSPACE_STORAGE_BACKEND=...)``
        would not re-evaluate it. We swap its ``_wrapped`` value directly and
        restore it on teardown. The default test backend is the dummy client
        whose presigned URLs point at a fake host; the fs backend's presigned
        URLs are real Django views the WSGI transport can serve.
        """
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)

        previous_wrapped = storage._wrapped
        storage._wrapped = FileSystemStorage(data_dir=tmpdir.name)
        self.addCleanup(lambda: setattr(storage, "_wrapped", previous_wrapped))

        assert isinstance(
            storage._wrapped, FileSystemStorage
        ), "filesystem storage swap failed — presigned URLs would be unreachable"

    # -- service-account helpers -------------------------------------------

    def _create_service_account(self, email: str) -> tuple[ServiceAccount, str]:
        """Create an active ServiceAccount, returning it and its raw token."""
        sa = ServiceAccount(email=email, is_active=True)
        raw_token = sa.generate_token()
        sa.save()
        return sa, raw_token

    def create_source_account(
        self, workspace: Workspace, role=WorkspaceMembershipRole.EDITOR
    ) -> str:
        """A SA that can read everything on the source workspace.

        EDITOR (or ADMIN) membership is the minimum that grants
        ``workspaces.update_connection``, without which the ``value`` resolver
        redacts secret fields and connection secrets would not copy.
        """
        sa, token = self._create_service_account(f"source-sa-{workspace.slug}@e2e.test")
        WorkspaceMembership.objects.create(user=sa, workspace=workspace, role=role)
        return token

    def create_target_account(
        self, organization: Organization, role=OrganizationMembershipRole.ADMIN
    ) -> str:
        """A SA that can create a workspace (and everything in it) on the target.

        Organization ADMIN satisfies ``create_workspace`` and, via
        ``is_organization_admin_or_owner``, the create perms for files,
        connections and pipelines on the workspace it creates.
        """
        sa, token = self._create_service_account(
            f"target-sa-{organization.id}@e2e.test"
        )
        OrganizationMembership.objects.create(
            organization=organization, user=sa, role=role
        )
        return token

    # -- source seeding ----------------------------------------------------

    def create_source_workspace(
        self,
        *,
        name="Source Workspace",
        description="A workspace to copy",
        countries=None,
        docker_image="blsq/openhexa-base:latest",
    ) -> Workspace:
        creator, _ = self._create_service_account("source-creator@e2e.test")
        OrganizationMembership.objects.create(
            organization=self.source_org,
            user=creator,
            role=OrganizationMembershipRole.ADMIN,
        )
        if countries is None:
            # Seed with real hexa Country instances (as the production
            # createWorkspace resolver does), whose codes therefore exist in the
            # Country table the target resolver validates against on the way back.
            countries = list(Country.objects.all()[:2])
        workspace = Workspace.objects.create_if_has_perm(
            creator,
            name=name,
            description=description,
            countries=countries,
            organization=self.source_org,
        )
        if docker_image:
            workspace.docker_image = docker_image
            workspace.save()
        return workspace

    def add_files(self, workspace: Workspace, files: dict[str, bytes]) -> None:
        """Write files into the workspace bucket through the storage backend."""
        for key, content in files.items():
            storage.save_object(workspace.bucket_name, key, content)

    def add_connection(
        self,
        workspace: Workspace,
        *,
        name="My Postgres",
        slug="my-postgres",
        connection_type=ConnectionType.POSTGRESQL,
        fields=None,
    ) -> Connection:
        admin, _ = self._create_service_account(f"conn-admin-{workspace.slug}@e2e.test")
        WorkspaceMembership.objects.create(
            user=admin, workspace=workspace, role=WorkspaceMembershipRole.ADMIN
        )
        if fields is None:
            fields = [
                {"code": "host", "value": "db.example.com", "secret": False},
                {"code": "password", "value": "s3cr3t", "secret": True},
            ]
        return Connection.objects.create_if_has_perm(
            admin,
            workspace,
            name=name,
            slug=slug,
            connection_type=connection_type,
            fields=fields,
        )

    def add_pipeline(
        self,
        workspace: Workspace,
        *,
        name="My Pipeline",
        version_names=("First", "Second"),
        parameters=None,
        schedule="0 6 * * *",
    ) -> Pipeline:
        """Seed a zipfile pipeline with versions, params and a scheduled version.

        The newest version is bound as ``scheduled_pipeline_version`` so the
        copier's "match the scheduled version on the target after re-numbering"
        path is exercised end to end.
        """
        creator, _ = self._create_service_account(
            f"pipe-creator-{workspace.slug}-{name}@e2e.test"
        )
        WorkspaceMembership.objects.create(
            user=creator, workspace=workspace, role=WorkspaceMembershipRole.ADMIN
        )
        if parameters is None:
            # required=False keeps versions schedulable, so binding the
            # scheduled version on the target succeeds.
            parameters = [
                {
                    "code": "year",
                    "name": "Year",
                    "type": "int",
                    "required": False,
                    "multiple": False,
                }
            ]
        pipeline = Pipeline.objects.create_if_has_perm(
            creator,
            workspace,
            name=name,
            schedule=schedule,
            type=PipelineType.ZIPFILE,
        )
        last_version = None
        for version_name in version_names:
            last_version = PipelineVersion.objects.create(
                pipeline=pipeline,
                user=creator,
                name=version_name,
                zipfile=_make_zipfile(version_name.encode()),
                parameters=parameters,
                config={},
            )
        pipeline.scheduled_pipeline_version = last_version
        pipeline.save()
        return pipeline

    # -- run ---------------------------------------------------------------

    def run_copy(
        self,
        *,
        source_slug: str,
        source_token: str,
        target_token: str,
        target_organization_id: str | None = None,
        target_workspace_name: str | None = None,
        target_workspace_slug: str | None = None,
        resources: set[str] | None = None,
        reporter=None,
    ):
        """Invoke the real ``run_copy`` with WSGI clients for both sides."""
        return run_copy(
            source_url=GRAPHQL_URL,
            source_token=source_token,
            source_slug=source_slug,
            target_url=GRAPHQL_URL,
            target_token=target_token,
            target_organization_id=target_organization_id,
            target_workspace_name=target_workspace_name,
            target_workspace_slug=target_workspace_slug,
            resources=resources,
            reporter=reporter or NullReporter(),
            http_client_factory=wsgi_client_factory,
        )
