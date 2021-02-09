class SyncResult:
    """Represents the result of a datasource sync operation performed by a connector"""

    def __init__(self, datasource, created, updated, identical):
        self.datasource = datasource
        self.created = created
        self.updated = updated
        self.identical = identical

    def __str__(self):
        figures = (
            f"{self.created} new, {self.updated} updated, {self.identical} unaffected"
        )

        return f'The datasource "{self.datasource.display_name}" has been synced ({figures})'

    def __add__(self, other):
        if other.datasource != self.datasource:
            raise ValueError(
                "The two SyncResults instances don't have the same datasource"
            )

        return SyncResult(
            datasource=self.datasource,
            created=self.created + other.created,
            updated=self.updated + other.updated,
            identical=self.identical + other.identical,
        )


class ContentSummary:
    """Summarize the content found in a datasource"""

    def __init__(self, **kwargs):
        self._counts = kwargs
        self.total = sum(count for _, count in self._counts.items())

    def __getattr__(self, item):
        try:
            return self._counts[item]
        except KeyError:
            raise AttributeError(f"{item} not found in ContentSummary instance")

    def __str__(self):
        return ", ".join([f"{name}, {count}(s)" for name, count in self._counts])
