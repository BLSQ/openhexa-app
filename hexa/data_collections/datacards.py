from django.http import HttpRequest
from django.utils.http import urlencode

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
        # TODO: Link this to a user perm
        return True

    def is_enabled(self, request: HttpRequest, model):
        return request.user.has_feature_flag("collections")

    def context(self, model, card):
        collections = get_item_value(
            model, self.source, container=card, exclude=datacard.Section
        )

        params = urlencode(
            {"redirect": card.request.path, "id": model.id, "type": self.graphql_type}
        )
        manage_url = f"/collections/add?{params}"

        return {
            "manage_url": manage_url,
            "collections": [
                {"name": collection.name, "url": f"/collections/{collection.id}"}
                for collection in collections
            ],
        }

    class Meta:
        model = Collection
