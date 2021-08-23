from django import test
from django.utils import timezone

from hexa.catalog.models import CatalogIndex
from ..models import Instance, DataElement


class ConnectorDhis2Test(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.DHIS2_INSTANCE_PLAY = Instance.objects.create(
            url="https://play.dhis2.org",
        )

    def test_delete_data_element(self):
        """Deleting a data element should delete its index as well"""

        data_element = DataElement.objects.create(
            name="some-data-element",
            external_access=False,
            favorite=False,
            created=timezone.now(),
            last_updated=timezone.now(),
            instance=self.DHIS2_INSTANCE_PLAY,
        )
        data_element_id = data_element.id
        self.assertEqual(
            1, CatalogIndex.objects.filter(object_id=data_element_id).count()
        )
        data_element.delete()
        self.assertEqual(
            0, CatalogIndex.objects.filter(object_id=data_element_id).count()
        )
