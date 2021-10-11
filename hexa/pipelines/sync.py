from hexa.pipelines.models import Environment


class EnvironmentSyncResult:
    """Represents the result of a datasource sync operation performed by a connector"""

    def __init__(
        self,
        *,
        environment: Environment,
        created: int = 0,
        updated: int = 0,
        identical: int = 0,
        orphaned: int = 0,
    ):
        self.environment = environment
        self.created = created
        self.updated = updated
        self.identical = identical
        self.orphaned = orphaned

    def __str__(self) -> str:
        figures = f"{self.created} new, {self.updated} updated, {self.identical} unaffected, {self.orphaned} orphaned"

        return f'The environment "{self.environment}" has been synced ({figures})'

    def __add__(self, other: "EnvironmentSyncResult") -> "EnvironmentSyncResult":
        if other.environment != self.environment:
            raise ValueError(
                "The two EnvironmentSyncResult instances don't have the same environment"
            )

        return EnvironmentSyncResult(
            environment=self.environment,
            created=self.created + other.created,
            updated=self.updated + other.updated,
            identical=self.identical + other.identical,
            orphaned=self.orphaned + other.orphaned,
        )

    def __eq__(self, o: "EnvironmentSyncResult") -> bool:
        return (
            self.environment == o.environment
            and self.created == o.created
            and self.updated == o.updated
            and self.identical == o.identical
            and self.orphaned == o.orphaned
        )

    def __repr__(self) -> str:
        return self.__str__()
