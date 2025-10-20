"""
Generic sorting utilities for GraphQL queries.
"""
from typing import Any, Dict, List, Optional

from django.db.models import QuerySet


class SortConfig:
    """Configuration for sortable fields on an entity."""

    def __init__(self, field_mapping: Dict[str, str], default_sort: List[str]):
        """
        Args:
            field_mapping: Maps GraphQL field names to Django ORM field names
                          e.g., {"NAME": "name", "CREATED_AT": "created_at"}
            default_sort: Default Django ORM ordering
                         e.g., ["name", "id"]
        """
        self.field_mapping = field_mapping
        self.default_sort = default_sort

    def get_order_by_fields(self, sort_input: Optional[Dict[str, Any]]) -> List[str]:
        """
        Convert GraphQL sort input to Django ORM order_by fields.

        Args:
            sort_input: Dict with 'field' and 'direction' keys
                       e.g., {"field": "NAME", "direction": "DESC"}

        Returns
        -------
            List of Django ORM field names for order_by()
            e.g., ["-name", "id"]
        """
        if not sort_input:
            return self.default_sort

        field = sort_input.get("field")
        direction = sort_input.get("direction", "ASC")

        if field not in self.field_mapping:
            return self.default_sort

        django_field = self.field_mapping[field]
        prefix = "-" if direction == "DESC" else ""

        # Add secondary sorting for stability
        secondary_sorts = self._get_secondary_sorts(django_field)

        return [f"{prefix}{django_field}"] + secondary_sorts

    def _get_secondary_sorts(self, primary_field: str) -> List[str]:
        """Add secondary sorting fields for tie-breaking."""
        if "name" in primary_field:
            return ["id"]
        else:
            return ["name", "id"]


def apply_sorting(
    queryset: QuerySet,
    sort_config: SortConfig,
    sort_input: Optional[Dict[str, Any]] = None,
) -> QuerySet:
    """
    Apply sorting to a Django QuerySet based on GraphQL input.

    Args:
        queryset: Django QuerySet to sort
        sort_config: SortConfig instance for the entity
        sort_input: Optional dict with 'field' and 'direction'

    Returns
    -------
        Sorted QuerySet

    Example:
        >>> config = SortConfig(
        ...     field_mapping={"NAME": "name", "CREATED_AT": "created_at"},
        ...     default_sort=["name", "id"]
        ... )
        >>> qs = apply_sorting(queryset, config, {"field": "NAME", "direction": "DESC"})
    """
    order_by_fields = sort_config.get_order_by_fields(sort_input)
    return queryset.order_by(*order_by_fields)
