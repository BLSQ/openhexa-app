from hexa.ui.datagrid import Column, Datagrid, DjangoModel


class CollectionColumn(Column):
    def __init__(self, *, value=None, max_items=2, **kwargs):
        super().__init__(**kwargs)

        self.value = value
        self.max_items = max_items

    def context(self, model: DjangoModel, grid: Datagrid):
        data = self.get_data(model, grid)

        return {
            "collections": data,
            "slice": f":{self.max_items}",
            "left_out": max(0, len(data) - self.max_items),
        }

    def get_data(self, model: DjangoModel, grid: Datagrid):
        return [
            {"label": collection.name, "url": collection.get_absolute_url()}
            for collection in self.get_value(model, self.value, container=Datagrid)
        ]

    @property
    def template(self):
        return "data_collections/datagrid/column_collection.html"
