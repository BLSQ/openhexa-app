from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import connection, models
from django.test import TestCase

from hexa.metadata.models import MetadataAttribute, MetadataMixin

User = get_user_model()


class TestModel(MetadataMixin, models.Model):
    """A simple model for testing the MetadataMixin"""

    name = models.CharField(max_length=100, default="test")

    def can_view_metadata(self, user):
        return True

    def can_update_metadata(self, user):
        return True

    def can_delete_metadata(self, user):
        return True

    class Meta:
        # This ensures the model only exists in the test database
        app_label = "metadata"


class MetadataMixinTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create the test table
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TestModel)
        # Create the content type for our test model
        ContentType.objects.get_or_create(
            app_label="metadata",
            model="testmodel",
        )

    @classmethod
    def tearDownClass(cls):
        # Delete the content type
        ContentType.objects.filter(
            app_label="metadata",
            model="testmodel",
        ).delete()
        # Drop the test table
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(TestModel)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create(email="test@example.com")
        self.test_obj = TestModel()
        self.test_obj.save()

    def test_update_or_create_attribute_creates_new(self):
        # Test creating a new attribute
        attr = self.test_obj.update_or_create_attribute(
            key="test_key", value="test_value", label="Test Label", principal=self.user
        )

        self.assertEqual(attr.key, "test_key")
        self.assertEqual(attr.value, "test_value")
        self.assertEqual(attr.label, "Test Label")
        self.assertEqual(attr.created_by, self.user)
        self.assertEqual(attr.updated_by, self.user)
        self.assertFalse(attr.system)

    def test_update_or_create_attribute_updates_existing(self):
        # First create an attribute
        attr1 = self.test_obj.update_or_create_attribute(
            key="test_key", value="initial_value", principal=self.user
        )

        # Then update it
        attr2 = self.test_obj.update_or_create_attribute(
            key="test_key", value="updated_value", principal=self.user
        )

        # Verify it's updated and not created new
        self.assertEqual(attr1.id, attr2.id)
        self.assertEqual(attr2.value, "updated_value")
        self.assertEqual(
            MetadataAttribute.objects.filter(
                object_id=self.test_obj.id, key="test_key"
            ).count(),
            1,
        )

    def test_delete_attribute(self):
        # Create an attribute
        self.test_obj.update_or_create_attribute(
            key="test_key", value="test_value", principal=self.user
        )

        # Delete it
        self.test_obj.delete_attribute("test_key")

        # Verify it's gone
        self.assertEqual(
            MetadataAttribute.objects.filter(
                object_id=self.test_obj.id, key="test_key"
            ).count(),
            0,
        )

    def test_system_attribute(self):
        # Test creating a system attribute
        attr = self.test_obj.update_or_create_attribute(
            key="system_key", value="system_value", system=True, principal=self.user
        )

        self.assertTrue(attr.system)

    def test_attribute_label(self):
        # Test attribute with label
        attr = self.test_obj.update_or_create_attribute(
            key="labeled_key", value="value", label="My Label", principal=self.user
        )

        self.assertEqual(attr.label, "My Label")

    def test_update_preserves_created_by(self):
        # Create with one user
        self.test_obj.update_or_create_attribute(
            key="test_key", value="initial_value", principal=self.user
        )

        # Create another user
        another_user = User.objects.create(email="another@example.com")

        # Update with different user
        attr2 = self.test_obj.update_or_create_attribute(
            key="test_key", value="new_value", principal=another_user
        )

        # created_by should still be the original user
        self.assertEqual(attr2.created_by, self.user)
        # updated_by should be the new user
        self.assertEqual(attr2.updated_by, another_user)
