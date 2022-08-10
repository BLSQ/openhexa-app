from hexa.ui import datacard
from hexa.ui.datacard import properties
from hexa.ui.utils import get_item_value

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

    def __init__(self, graphql_type, value=None, **kwargs):
        super().__init__(**kwargs)
        self.graphql_type = graphql_type
        self.source = value

    @property
    def template(self):
        return "data_collections/datacard/section_collections.html"

    @property
    def is_editable(self):
        # TODO
        return True

    def context(self, model, card):
        collections = get_item_value(
            model, self.source, container=card, exclude=datacard.Section
        )
        return {
            "manage_url": f"/collections/add?type={self.graphql_type}&id={model.id}",
            "collections": [
                {"name": collection.name, "url": f"/collections/{collection.id}"}
                for collection in collections
            ],
        }

    class Meta:
        model = Collection
