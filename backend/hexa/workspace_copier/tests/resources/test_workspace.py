from types import SimpleNamespace
from unittest.mock import MagicMock

from django.test import SimpleTestCase

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.resources.workspace import WorkspaceMetadataCopier
from hexa.workspace_copier.results import CopyResult
from hexa.workspace_copier.transport import GraphQLError


def _src_ws(**overrides):
    data = {
        "name": "My Workspace",
        "description": "desc",
        "countries": [],
        "configuration": {},
        "docker_image": None,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


class WorkspaceMetadataCopierRemoteTest(SimpleTestCase):
    def test_creates_remote_target_and_stores_slug(self):
        source = Endpoint.remote(MagicMock(), "src")
        source.client.workspace.return_value = _src_ws()
        target = Endpoint.remote(MagicMock())
        target.client.create_workspace.return_value = MagicMock(
            success=True, workspace=SimpleNamespace(slug="my-workspace-ab12")
        )
        result = CopyResult()

        WorkspaceMetadataCopier().copy(source, target, result, NullReporter())

        self.assertEqual(target.slug, "my-workspace-ab12")
        self.assertEqual(result.workspace_slug, "my-workspace-ab12")
        self.assertEqual(result.workspace_name, "My Workspace")

    def test_sets_docker_image_when_present(self):
        source = Endpoint.remote(MagicMock(), "src")
        source.client.workspace.return_value = _src_ws(docker_image="custom:1")
        target = Endpoint.remote(MagicMock())
        target.client.create_workspace.return_value = MagicMock(
            success=True, workspace=SimpleNamespace(slug="slug")
        )
        target.client.update_workspace.return_value = MagicMock(success=True)
        result = CopyResult()

        WorkspaceMetadataCopier().copy(source, target, result, NullReporter())

        target.client.update_workspace.assert_called_once()

    def test_missing_source_workspace_raises(self):
        source = Endpoint.remote(MagicMock(), "missing")
        source.client.workspace.return_value = None
        target = Endpoint.remote(MagicMock())

        with self.assertRaises(GraphQLError):
            WorkspaceMetadataCopier().copy(
                source, target, CopyResult(), NullReporter()
            )

    def test_local_target_not_yet_implemented(self):
        source = Endpoint.remote(MagicMock(), "src")
        source.client.workspace.return_value = _src_ws()
        target = Endpoint.local()

        with self.assertRaises(NotImplementedError):
            WorkspaceMetadataCopier().copy(
                source, target, CopyResult(), NullReporter()
            )
