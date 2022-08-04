from hexa.ui import datacard
from hexa.ui.datacard import properties

from .models import Collection


class CollectionProperty(properties.Property):
    def __init__(self, *, value=None, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    @property
    def template(self):
        return "data_collections/datacard/property_collection.html"

    def context(self, model, section):
        return {
            "collections": [
                {"name": c.name, "url": c.get_absolute_url()}
                for c in self.get_value(model, self.value, container=section)
            ],
        }


class CollectionsSection(datacard.Section):
    title = "Collections"

    collections = CollectionProperty(value="collections.all")

    class Meta:
        model = Collection
