from django.http import HttpRequest

from hexa.ui.datagrid import Column, Datagrid, DjangoModel

from .models import CollectionElement


class CollectionColumn(Column):
    def __init__(self, *, max_items=2, **kwargs):
        super().__init__(**kwargs)

        self.max_items = max_items

    def context(self, model: DjangoModel, grid: Datagrid):
        data = self.get_data(model, grid)

        return {
            "collections": data,
            "slice": f":{self.max_items}",
            "left_out": max(0, len(data) - self.max_items),
        }

    def get_data(self, model: DjangoModel, grid: Datagrid):
        elements = (
            CollectionElement.objects.filter_for_user(grid.request.user)
            .filter_for_object(model)
            .order_by("-updated_at")
            .select_related("collection")
        )

        return [
            {
                "label": element.collection.name,
                "url": element.collection.get_absolute_url(),
            }
            for element in elements
        ]

    def is_enabled(self, request: HttpRequest):
        return request.user.has_feature_flag("collections")

    @property
    def template(self):
        return "data_collections/datagrid/column_collection.html"
