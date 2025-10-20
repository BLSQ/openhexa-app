from hexa.core.graphql.sorting import SortConfig, apply_sorting
from hexa.core.test import TestCase
from hexa.workspaces.models import Workspace


class SortingTestCase(TestCase):
    def test_sort_config_default_sort(self):
        config = SortConfig(
            field_mapping={"NAME": "name", "CREATED_AT": "created_at"},
            default_sort=["name", "id"],
        )
        order_by_fields = config.get_order_by_fields(None)
        self.assertEqual(order_by_fields, ["name", "id"])

    def test_sort_config_ascending(self):
        config = SortConfig(
            field_mapping={"NAME": "name", "CREATED_AT": "created_at"},
            default_sort=["name", "id"],
        )
        order_by_fields = config.get_order_by_fields(
            {"field": "NAME", "direction": "ASC"}
        )
        self.assertEqual(order_by_fields, ["name", "id"])

    def test_sort_config_descending(self):
        config = SortConfig(
            field_mapping={"NAME": "name", "CREATED_AT": "created_at"},
            default_sort=["name", "id"],
        )
        order_by_fields = config.get_order_by_fields(
            {"field": "NAME", "direction": "DESC"}
        )
        self.assertEqual(order_by_fields, ["-name", "id"])

    def test_sort_config_secondary_sorts_for_name(self):
        config = SortConfig(field_mapping={"NAME": "name"}, default_sort=["name", "id"])
        order_by_fields = config.get_order_by_fields(
            {"field": "NAME", "direction": "ASC"}
        )
        self.assertEqual(order_by_fields, ["name", "id"])

    def test_sort_config_secondary_sorts_for_created_at(self):
        config = SortConfig(
            field_mapping={"CREATED_AT": "created_at"},
            default_sort=["created_at", "id"],
        )
        order_by_fields = config.get_order_by_fields(
            {"field": "CREATED_AT", "direction": "DESC"}
        )
        self.assertEqual(order_by_fields, ["-created_at", "name", "id"])

    def test_sort_config_secondary_sorts_for_count_field(self):
        config = SortConfig(
            field_mapping={"COUNT": "pipelines_count"}, default_sort=["name", "id"]
        )
        order_by_fields = config.get_order_by_fields(
            {"field": "COUNT", "direction": "DESC"}
        )
        self.assertEqual(order_by_fields, ["-pipelines_count", "name", "id"])

    def test_sort_config_invalid_field_returns_default(self):
        config = SortConfig(field_mapping={"NAME": "name"}, default_sort=["name", "id"])
        order_by_fields = config.get_order_by_fields(
            {"field": "INVALID", "direction": "ASC"}
        )
        self.assertEqual(order_by_fields, ["name", "id"])

    def test_apply_sorting_with_queryset(self):
        Workspace.objects.create(name="Alpha Workspace", slug="alpha", db_name="alpha")
        Workspace.objects.create(name="Beta Workspace", slug="beta", db_name="beta")
        Workspace.objects.create(name="Gamma Workspace", slug="gamma", db_name="gamma")

        config = SortConfig(field_mapping={"NAME": "name"}, default_sort=["name"])
        queryset = Workspace.objects.all()

        sorted_qs = apply_sorting(
            queryset, config, {"field": "NAME", "direction": "ASC"}
        )

        names = list(sorted_qs.values_list("name", flat=True))
        self.assertEqual(
            names, ["Alpha Workspace", "Beta Workspace", "Gamma Workspace"]
        )

    def test_apply_sorting_descending_with_queryset(self):
        Workspace.objects.create(name="Alpha Workspace", slug="alpha", db_name="alpha")
        Workspace.objects.create(name="Beta Workspace", slug="beta", db_name="beta")
        Workspace.objects.create(name="Gamma Workspace", slug="gamma", db_name="gamma")

        config = SortConfig(field_mapping={"NAME": "name"}, default_sort=["name"])
        queryset = Workspace.objects.all()

        sorted_qs = apply_sorting(
            queryset, config, {"field": "NAME", "direction": "DESC"}
        )

        names = list(sorted_qs.values_list("name", flat=True))
        self.assertEqual(
            names, ["Gamma Workspace", "Beta Workspace", "Alpha Workspace"]
        )

    def test_apply_sorting_uses_default_when_no_sort_input(self):
        Workspace.objects.create(name="Gamma Workspace", slug="gamma", db_name="gamma")
        Workspace.objects.create(name="Alpha Workspace", slug="alpha", db_name="alpha")

        config = SortConfig(field_mapping={"NAME": "name"}, default_sort=["name"])
        queryset = Workspace.objects.all()

        sorted_qs = apply_sorting(queryset, config, None)

        names = list(sorted_qs.values_list("name", flat=True))
        self.assertEqual(names, ["Alpha Workspace", "Gamma Workspace"])
