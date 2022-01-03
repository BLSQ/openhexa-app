from hexa.catalog.models import Datasource


class DatasourceSyncResult:
    """Represents the result of a datasource sync operation performed by a connector"""

    def __init__(
        self,
        *,
        datasource: Datasource,
        created: int = 0,
        updated: int = 0,
        identical: int = 0,
        deleted: int = 0,
    ):
        self.datasource = datasource
        self.created = created
        self.updated = updated
        self.identical = identical
        self.deleted = deleted

    def __str__(self) -> str:
        figures = f"{self.created} new, {self.updated} updated, {self.identical} unaffected, {self.deleted} deleted"

        return f'The datasource "{self.datasource}" has been synced ({figures})'

    def __add__(self, other: "DatasourceSyncResult") -> "DatasourceSyncResult":
        if other.datasource != self.datasource:
            raise ValueError(
                "The two DatasourceSyncResult instances don't have the same datasource"
            )

        return DatasourceSyncResult(
            datasource=self.datasource,
            created=self.created + other.created,
            updated=self.updated + other.updated,
            identical=self.identical + other.identical,
            deleted=self.deleted + other.deleted,
        )

    def __eq__(self, o: "DatasourceSyncResult") -> bool:
        return (
            self.datasource == o.datasource
            and self.created == o.created
            and self.updated == o.updated
            and self.identical == o.identical
            and self.deleted == o.deleted
        )

    def __repr__(self) -> str:
        return self.__str__()
