from django.db import connection

from hexa.core.test import TestCase

from .models import TestMyModel


class TestSoftDeleteModel(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TestMyModel)

    @classmethod
    def tearDownClass(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(TestMyModel)

        super().tearDownClass()

    def test_soft_delete_model(self):
        my_model = TestMyModel.objects.create()

        self.assertFalse(my_model.is_deleted)
        self.assertFalse(my_model.is_restored)
        my_model.delete()

        self.assertTrue(my_model.is_deleted)
        self.assertEqual(TestMyModel.objects.count(), 0)
        self.assertEqual(TestMyModel.all_objects.count(), 1)

    def test_restore_soft_deleted_model(self):
        my_model = TestMyModel.objects.create()
        my_model.delete()

        self.assertTrue(my_model.is_deleted)
        self.assertFalse(my_model.is_restored)

        my_model.restore()

        self.assertFalse(my_model.is_deleted)
        self.assertTrue(my_model.is_restored)
        self.assertEqual(TestMyModel.objects.count(), 1)

    def test_hard_delete_model(self):
        my_model = TestMyModel.objects.create()
        my_model.hard_delete()

        self.assertEqual(TestMyModel.objects.count(), 0)
        self.assertEqual(TestMyModel.all_objects.count(), 0)

    def test_soft_delete_queryset(self):
        TestMyModel.objects.create()
        TestMyModel.objects.create()

        self.assertEqual(TestMyModel.objects.count(), 2)

        # call the soft delete method on all objects in the qs
        TestMyModel.objects.delete()

        self.assertEqual(TestMyModel.objects.count(), 0)
        self.assertEqual(TestMyModel.all_objects.count(), 2)

    def test_hard_delete_queryset(self):
        TestMyModel.objects.create()
        TestMyModel.objects.create()

        self.assertEqual(TestMyModel.objects.count(), 2)

        # call the delete method on all objects in the qs
        TestMyModel.objects.hard_delete()
        self.assertEqual(TestMyModel.objects.count(), 0)
        self.assertEqual(TestMyModel.all_objects.count(), 0)
