class DatasourceSyncResult:
    """Represents the result of a datasource sync operation performed by a connector"""

    def __init__(self, *, datasource, created=0, updated=0, identical=0, orphaned=0):
        self.datasource = datasource
        self.created = created
        self.updated = updated
        self.identical = identical
        self.orphaned = orphaned

    def __str__(self):
        figures = f"{self.created} new, {self.updated} updated, {self.identical} unaffected, {self.orphaned} orphaned"

        return f'The datasource "{self.datasource}" has been synced ({figures})'

    def __add__(self, other):
        if other.datasource != self.datasource:
            raise ValueError(
                "The two DatasourceSyncResult instances don't have the same datasource"
            )

        return DatasourceSyncResult(
            datasource=self.datasource,
            created=self.created + other.created,
            updated=self.updated + other.updated,
            identical=self.identical + other.identical,
            orphaned=self.orphaned + other.orphaned,
        )
