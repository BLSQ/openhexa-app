from django.core.exceptions import PermissionDenied
from django_countries.fields import Country

from hexa.core.test import TestCase
from hexa.data_collections.models import Collection
from hexa.user_management.models import User


class ModelsTest(TestCase):
    USER_MARK = None
    COLLECTION_COVID = None
    COLLECTION_MALARIA = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_MARK = User.objects.create_user(
            "mark@bluesquarehub.com",
            "markspassword",
        )
        cls.USER_JOHN = User.objects.create_user(
            "john@bluesquarehub.com", "johnpassword"
        )
        cls.COLLECTION_COVID = Collection.objects.create(
            name="Covid", author=cls.USER_MARK
        )
        cls.COLLECTION_MALARIA = Collection.objects.create(name="Malaria")

    def test_create_collection_if_has_perm(self):
        collection = Collection.objects.create_if_has_perm(
            self.USER_MARK,
            name="A collection",
            description="A great collection",
            countries=[Country("BE"), Country("DE")],
        )
        self.assertIsInstance(collection, Collection)
        self.assertEqual("A collection", collection.name)
        self.assertEqual("A great collection", collection.description)
        self.assertEqual([Country("BE"), Country("DE")], collection.countries)
        self.assertEqual(0, collection.tags.count())
        self.assertIsNone(collection.author)

    def test_update_collection_if_has_perm(self):
        self.COLLECTION_COVID.update_if_has_perm(self.USER_MARK)

        with self.assertRaises(PermissionDenied):
            self.COLLECTION_COVID.update_if_has_perm(
                self.USER_JOHN, name="New collection title"
            )

    def test_filter_for_user(self):
        self.assertEqual(2, Collection.objects.filter_for_user(self.USER_MARK).count())

    def test_delete_if_has_perm(self):
        self.assertEqual(1, Collection.objects.filter(name="Covid").count())
        self.COLLECTION_COVID.delete_if_has_perm(self.USER_MARK)
        self.assertEqual(0, Collection.objects.filter(name="Covid").count())
