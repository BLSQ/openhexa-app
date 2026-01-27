from rest_framework import serializers


class TableDataSerializer(serializers.Serializer):
    """Serializer for table data query parameters and response"""

    # Query parameters
    page = serializers.IntegerField(default=1, min_value=1)
    limit = serializers.IntegerField(default=10, min_value=1, max_value=10000)
    sort = serializers.CharField(required=False, allow_blank=True)
    direction = serializers.ChoiceField(choices=["asc", "desc"], default="asc", required=False)
    format = serializers.ChoiceField(choices=["json", "csv"], default="json", required=False)

    def validate_sort(self, value):
        """Validate sort column name"""
        if value and not value.replace("_", "").isalnum():
            raise serializers.ValidationError(
                "Sort column name must be alphanumeric with underscores"
            )
        return value


class ColumnFilterSerializer(serializers.Serializer):
    """Serializer for dynamic column filters"""

    column = serializers.CharField()
    value = serializers.CharField()

    def validate_column(self, value):
        """Validate column name"""
        if not value.replace("_", "").isalnum():
            raise serializers.ValidationError("Column name must be alphanumeric with underscores")
        return value


class RecipeExecuteSerializer(serializers.Serializer):
    """
    Validate query params for executing a recipe.

    We accept:
    - format: json or csv
    - limit: optional safety cap (still bounded by server-side max)
    - any recipe parameter: passed through and substituted in SQL template
    - column filters with operators (e.g., date__gte, status__eq): applied to result set
      Supported operators: eq, neq, gt, gte, lt, lte, contains, icontains,
      startswith, endswith
    """

    format = serializers.ChoiceField(
        choices=["json", "csv"], required=False, default="json"
    )
    limit = serializers.IntegerField(required=False, min_value=1, max_value=50000)


class RecipeCreateUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    sql_template = serializers.CharField()
    is_active = serializers.BooleanField(required=False, default=True)
