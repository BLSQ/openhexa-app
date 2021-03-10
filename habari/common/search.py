from django.utils.translation import ugettext_lazy as _
from django.utils.timesince import timesince


class SearchResult:
    """Each app can provide one or more subclasses of this class to plug to the search engine."""

    def __init__(self, model):
        self.model = model

    @property
    def object_id(self):
        return self.model.pk

    @property
    def rank(self):
        return self.model.rank

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
    def label(self):
        raise NotImplementedError(
            "Each SearchResult subclass should implement a label() property"
        )

    @property
    def origin(self):
        raise NotImplementedError(
            "Each SearchResult subclass should implement a origin() property"
        )

    @property
    def updated_at(self):
        raise NotImplementedError(
            "Each SearchResult subclass should implement a updated_at() property"
        )

    @property
    def detail_url(self):
        raise NotImplementedError(
            "Each SearchResult subclass should implement a detail_url() property"
        )

    @property
    def symbol(self):
        raise NotImplementedError(
            "Each SearchResult subclass should implement a symbol() property"
        )

    def to_dict(self):
        return {
            "id": self.object_id,
            "rank": self.rank,
            "result_type": self.result_type,
            "title": self.title,
            "label": self.label,
            "origin": self.origin,
            "detail_url": self.detail_url,
            "updated_at": f"{timesince(self.updated_at)} {_('ago')}",
            "symbol": self.symbol,
        }
