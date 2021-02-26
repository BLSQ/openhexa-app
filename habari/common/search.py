class SearchResult:
    """Each app can provide one or more subclasses of this class to plug to the search engine."""

    def __init__(self, model):
        self.model = model

    @property
    def title(self):
        raise NotImplementedError(
            "Each SearchResult subclass should implement a title() property"
        )

    @property
    def result_type(self):
        raise NotImplementedError(
            "Each SearchResult subclass should implement a result_type() property"
        )

    @property
    def result_label(self):
        raise NotImplementedError(
            "Each SearchResult subclass should implement a result_label() property"
        )

    @property
    def object_id(self):
        return self.model.pk

    @property
    def areas(self):
        return list(self.model.areas.all())

    @property
    def themes(self):
        return list(self.model.themes.all())

    def to_dict(self):
        return {
            "id": self.object_id,
            "result_type": self.result_type,
            "result_label": self.result_label,
            "title": self.title,
            "areas": [
                {
                    "id": area.pk,
                    "name": area.name,
                    "short_name": area.short_name,
                    "description": area.description,
                }
                for area in self.areas
            ],
            "themes": [
                {
                    "id": theme.pk,
                    "name": theme.name,
                    "short_name": theme.short_name,
                    "description": theme.description,
                }
                for theme in self.themes
            ],
        }
