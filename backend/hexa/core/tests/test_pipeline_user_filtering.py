"""
Unit tests for PipelineRunUser filtering in changed QuerySets.

Tests that the updated QuerySets properly handle PipelineRunUser through 
the generic BaseQuerySet._filter_for_user_and_query_object method.
"""
from unittest.mock import Mock, patch

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from hexa.user_management.models import User


class MockPipelineRunUser:
    """Mock PipelineRunUser for testing"""

    def __init__(self, workspace_id):
        self.pipeline_run = Mock()
        self.pipeline_run.pipeline = Mock()
        self.pipeline_run.pipeline.workspace = Mock()
        self.pipeline_run.pipeline.workspace.id = workspace_id
        self.is_authenticated = True
        self.is_superuser = False

    @property
    def __class__(self):
        # Mock class with correct name for isinstance checks
        mock_class = Mock()
        mock_class.__name__ = "PipelineRunUser"
        return mock_class


class TestPipelineRunUserFiltering(TestCase):
    """Test PipelineRunUser filtering in updated QuerySets"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
        self.workspace_id = "workspace-123"
        self.pipeline_user = MockPipelineRunUser(self.workspace_id)

    def test_dataset_link_queryset_filter_for_user(self):
        """Test DatasetLinkQuerySet.filter_for_user works with PipelineRunUser"""
        from hexa.datasets.models import DatasetLinkQuerySet

        with patch.object(
            DatasetLinkQuerySet, "_filter_for_user_and_query_object"
        ) as mock_filter:
            queryset = DatasetLinkQuerySet()
            queryset.filter_for_user(self.pipeline_user)

            # Should call _filter_for_user_and_query_object with PipelineRunUser
            mock_filter.assert_called_once()
            call_args = mock_filter.call_args[0]
            self.assertEqual(call_args[0], self.pipeline_user)
            # Query should be for workspace__members=user
            self.assertIn("workspace__members", str(call_args[1]))

    def test_workspace_queryset_filter_for_user(self):
        """Test WorkspaceQuerySet.filter_for_user works with PipelineRunUser"""
        from hexa.workspaces.models import WorkspaceQuerySet

        with patch.object(
            WorkspaceQuerySet, "_filter_for_user_and_query_object"
        ) as mock_filter:
            queryset = WorkspaceQuerySet()
            queryset.filter_for_user(self.pipeline_user)

            # Should call _filter_for_user_and_query_object with PipelineRunUser
            mock_filter.assert_called_once()
            call_args = mock_filter.call_args[0]
            self.assertEqual(call_args[0], self.pipeline_user)
            # Query should be for workspacemembership__user=user and archived=False
            query_str = str(call_args[1])
            self.assertIn("workspacemembership__user", query_str)
            self.assertIn("archived", query_str)

    def test_connection_queryset_filter_for_user(self):
        """Test ConnectionQuerySet.filter_for_user works with PipelineRunUser"""
        from hexa.workspaces.models import ConnectionQuerySet

        with patch.object(
            ConnectionQuerySet, "_filter_for_user_and_query_object"
        ) as mock_filter:
            queryset = ConnectionQuerySet()
            queryset.filter_for_user(self.pipeline_user)

            # Should call _filter_for_user_and_query_object with PipelineRunUser
            mock_filter.assert_called_once()
            call_args = mock_filter.call_args[0]
            self.assertEqual(call_args[0], self.pipeline_user)
            # Query should be for workspace__members=user
            self.assertIn("workspace__members", str(call_args[1]))

    def test_organization_queryset_has_custom_workspace_query(self):
        """Test OrganizationQuerySet has custom _get_pipeline_run_user_workspace_query"""
        from hexa.user_management.models import OrganizationQuerySet

        queryset = OrganizationQuerySet()
        query = queryset._get_pipeline_run_user_workspace_query(self.pipeline_user)

        # Should use workspaces__in= instead of workspace=
        self.assertIn("workspaces__in", str(query))

    def test_workspace_queryset_has_custom_workspace_query(self):
        """Test WorkspaceQuerySet has custom _get_pipeline_run_user_workspace_query"""
        from hexa.workspaces.models import WorkspaceQuerySet

        queryset = WorkspaceQuerySet()
        query = queryset._get_pipeline_run_user_workspace_query(self.pipeline_user)

        # Should use id= and archived=False
        query_str = str(query)
        self.assertIn("id", query_str)
        self.assertIn("archived", query_str)

    def test_regular_user_filtering_unchanged(self):
        """Test that regular user filtering still works as before"""
        from hexa.datasets.models import DatasetLinkQuerySet

        with patch.object(
            DatasetLinkQuerySet, "_filter_for_user_and_query_object"
        ) as mock_filter:
            queryset = DatasetLinkQuerySet()
            queryset.filter_for_user(self.user)

            # Should call _filter_for_user_and_query_object with regular user
            mock_filter.assert_called_once()
            call_args = mock_filter.call_args[0]
            self.assertEqual(call_args[0], self.user)

    def test_anonymous_user_filtering_unchanged(self):
        """Test that anonymous user filtering still works as before"""
        from hexa.datasets.models import DatasetLinkQuerySet

        with patch.object(
            DatasetLinkQuerySet, "_filter_for_user_and_query_object"
        ) as mock_filter:
            queryset = DatasetLinkQuerySet()
            anonymous = AnonymousUser()
            queryset.filter_for_user(anonymous)

            # Should call _filter_for_user_and_query_object with anonymous user
            mock_filter.assert_called_once()
            call_args = mock_filter.call_args[0]
            self.assertEqual(call_args[0], anonymous)


class TestBaseQuerySetPipelineRunUserDetection(TestCase):
    """Test that BaseQuerySet correctly detects and handles PipelineRunUser"""

    def setUp(self):
        self.workspace_id = "workspace-123"
        self.pipeline_user = MockPipelineRunUser(self.workspace_id)

    def test_pipeline_run_user_class_name_detection(self):
        """Test PipelineRunUser detection by class name"""
        from hexa.core.models.base import BaseQuerySet

        # Mock a simple model with workspace field
        mock_model = Mock()
        mock_model._meta.get_field.return_value = Mock()  # workspace field exists

        queryset = BaseQuerySet(model=mock_model)

        with patch.object(queryset, "filter") as mock_filter, patch.object(
            queryset, "distinct"
        ) as mock_distinct:
            mock_filter.return_value = queryset
            mock_distinct.return_value = queryset

            # Call _filter_for_user_and_query_object with PipelineRunUser
            queryset._filter_for_user_and_query_object(
                self.pipeline_user,
                Mock(),  # Regular query object (should be ignored)
            )

            # Should detect PipelineRunUser and use workspace-based filtering
            mock_filter.assert_called_once()
            mock_distinct.assert_called_once()

    def test_regular_user_not_detected_as_pipeline_user(self):
        """Test that regular users are not detected as PipelineRunUser"""
        from hexa.core.models.base import BaseQuerySet
        from hexa.user_management.models import User

        user = User.objects.create_user(email="test@example.com", password="pass")
        mock_model = Mock()
        queryset = BaseQuerySet(model=mock_model)

        with patch.object(queryset, "filter") as mock_filter, patch.object(
            queryset, "distinct"
        ) as mock_distinct:
            mock_filter.return_value = queryset
            mock_distinct.return_value = queryset

            test_query = Mock()
            queryset._filter_for_user_and_query_object(user, test_query)

            # Should use the provided query, not workspace filtering
            mock_filter.assert_called_once_with(test_query)
            mock_distinct.assert_called_once()
