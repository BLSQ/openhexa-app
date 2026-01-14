import csv
import io

import psycopg2
from django.http import HttpResponse
from psycopg2 import sql
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from hexa.workspaces.models import Workspace

from .authentication import WorkspaceTokenAuthentication
from .models import DatasetRecipe
from .permissions import view_database_tables
from .serializers import (
    RecipeCreateUpdateSerializer,
    RecipeExecuteSerializer,
    TableDataSerializer,
)
from .utils import (
    execute_recipe_query,
    get_table_definition,
    get_workspace_database_connection,
    render_recipe_sql,
    validate_recipe_parameters,
)


class TableDataAPIView(APIView):
    """
    REST API endpoint for querying workspace database tables with filtering, pagination, and sorting.

    URL: /api/workspace/<workspace_slug>/database/<db_name>/table/<table_name>/
    """

    # Support both session auth (web) and token auth (API)
    authentication_classes = [SessionAuthentication, WorkspaceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, workspace_slug, db_name, table_name):
        """
        GET endpoint to fetch table data with optional filtering, sorting, and pagination.

        Query Parameters:
        - page: Page number (default: 1)
        - limit: Results per page (default: 10, max: 1000)
        - sort: Column name to sort by
        - direction: Sort direction ('asc' or 'desc', default: 'asc')
        - format: Response format ('json' or 'csv', default: 'json')
        - Any column name for filtering (e.g., ?country=bel)
        """
        # Validate workspace access
        try:
            workspace = Workspace.objects.filter_for_user(request.user).get(slug=workspace_slug)
        except Workspace.DoesNotExist:
            return Response(
                {"error": "Workspace not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check permission to view database tables
        if not view_database_tables(request.user, workspace):
            return Response(
                {"error": "Permission denied to view database tables"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Verify database belongs to workspace
        if workspace.db_name != db_name:
            return Response(
                {"error": "Database does not belong to this workspace"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate query parameters
        serializer = TableDataSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        page = validated_data.get("page", 1)
        limit = validated_data.get("limit", 10)
        sort_column = validated_data.get("sort", None)
        direction = validated_data.get("direction", "asc").upper()
        output_format = validated_data.get("format", "json")

        # Get table definition to validate table exists and get columns
        table_def = get_table_definition(workspace, table_name)
        if not table_def:
            return Response(
                {"error": f"Table '{table_name}' not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get available columns
        available_columns = {col["name"]: col["type"] for col in table_def["columns"]}

        # Parse column filters from query params with operators
        column_filters = []
        reserved_params = {"page", "limit", "sort", "direction", "format"}

        # Supported operators with their SQL equivalents
        operator_map = {
            "eq": "=",  # Equal (default)
            "neq": "!=",  # Not equal
            "gt": ">",  # Greater than
            "gte": ">=",  # Greater than or equal
            "lt": "<",  # Less than
            "lte": "<=",  # Less than or equal
            "contains": "LIKE",  # Contains (case-sensitive)
            "icontains": "ILIKE",  # Contains (case-insensitive)
            "startswith": "LIKE",  # Starts with
            "endswith": "LIKE",  # Ends with
        }

        for param_name, param_value in request.query_params.items():
            if param_name not in reserved_params:
                # Parse parameter: column__operator or just column (defaults to eq)
                if "__" in param_name:
                    column_name, operator = param_name.rsplit("__", 1)
                    if operator not in operator_map:
                        return Response(
                            {
                                "error": f"Invalid operator '{operator}'. Supported: {', '.join(operator_map.keys())}"
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                else:
                    column_name = param_name
                    operator = "eq"

                # Validate column exists
                if column_name not in available_columns:
                    return Response(
                        {"error": f"Column '{column_name}' does not exist in table"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                column_filters.append(
                    {
                        "column": column_name,
                        "operator": operator,
                        "value": param_value,
                    }
                )

        # Validate sort column if provided
        if sort_column and sort_column not in available_columns:
            return Response(
                {"error": f"Sort column '{sort_column}' does not exist in table"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Build and execute query
        try:
            data, total_rows = self._fetch_table_data(
                workspace=workspace,
                table_name=table_name,
                page=page,
                limit=limit,
                sort_column=sort_column,
                direction=direction,
                column_filters=column_filters,
            )
        except Exception as e:
            return Response(
                {"error": f"Database query failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Calculate pagination metadata
        total_pages = (total_rows + limit - 1) // limit  # Ceiling division
        has_next = page < total_pages
        has_previous = page > 1

        # Format response
        response_data = {
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_rows": total_rows,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_previous": has_previous,
            },
            "columns": list(available_columns.keys()),
            "table": table_name,
            "workspace": workspace_slug,
            "database": db_name,
        }

        # Return response in requested format
        if output_format == "csv":
            return self._generate_csv_response(data, list(available_columns.keys()))
        else:
            return Response(response_data, status=status.HTTP_200_OK)

    def _fetch_table_data(
        self,
        workspace,
        table_name,
        page,
        limit,
        sort_column,
        direction,
        column_filters,
    ):
        """
        Fetch table data with filters, sorting, and pagination.

        Returns tuple of (data, total_rows)
        """
        # Operator mapping
        operator_map = {
            "eq": "=",
            "neq": "!=",
            "gt": ">",
            "gte": ">=",
            "lt": "<",
            "lte": "<=",
            "contains": "LIKE",
            "icontains": "ILIKE",
            "startswith": "LIKE",
            "endswith": "LIKE",
        }

        conn = None
        try:
            conn = get_workspace_database_connection(workspace)
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Build WHERE clause for column filters
                where_conditions = []
                where_params = []

                for filter_item in column_filters:
                    col_name = filter_item["column"]
                    operator = filter_item["operator"]
                    col_value = filter_item["value"]

                    # Get SQL operator
                    sql_operator = operator_map[operator]

                    # Handle LIKE operators with pattern matching
                    if operator == "contains" or operator == "icontains":
                        where_conditions.append(
                            sql.SQL("{column} " + sql_operator + " %s").format(
                                column=sql.Identifier(col_name)
                            )
                        )
                        where_params.append(f"%{col_value}%")
                    elif operator == "startswith":
                        where_conditions.append(
                            sql.SQL("{column} " + sql_operator + " %s").format(
                                column=sql.Identifier(col_name)
                            )
                        )
                        where_params.append(f"{col_value}%")
                    elif operator == "endswith":
                        where_conditions.append(
                            sql.SQL("{column} " + sql_operator + " %s").format(
                                column=sql.Identifier(col_name)
                            )
                        )
                        where_params.append(f"%{col_value}")
                    else:
                        # Standard comparison operators
                        where_conditions.append(
                            sql.SQL("{column} " + sql_operator + " %s").format(
                                column=sql.Identifier(col_name)
                            )
                        )
                        where_params.append(col_value)

                # Build WHERE clause SQL
                if where_conditions:
                    where_clause = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(where_conditions)
                else:
                    where_clause = sql.SQL("")

                # Get total count with filters applied
                count_query = sql.SQL("SELECT COUNT(*) as total FROM {table}{where}").format(
                    table=sql.Identifier(table_name), where=where_clause
                )
                cursor.execute(count_query, where_params)
                total_rows = cursor.fetchone()["total"]

                # Build ORDER BY clause
                if sort_column:
                    order_clause = sql.SQL(" ORDER BY {column} {direction}").format(
                        column=sql.Identifier(sort_column),
                        direction=sql.SQL(direction),
                    )
                else:
                    order_clause = sql.SQL("")

                # Build SELECT query with pagination
                offset = (page - 1) * limit
                select_query = sql.SQL(
                    "SELECT * FROM {table}{where}{order} LIMIT %s OFFSET %s"
                ).format(
                    table=sql.Identifier(table_name),
                    where=where_clause,
                    order=order_clause,
                )

                cursor.execute(select_query, where_params + [limit, offset])
                data = cursor.fetchall()

                # Convert RealDictRow to regular dict for JSON serialization
                data = [dict(row) for row in data]

                return data, total_rows
        finally:
            if conn:
                conn.close()

    def _generate_csv_response(self, data, columns):
        """Generate CSV response from table data"""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(data)

        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="table_data.csv"'
        return response


class DatasetRecipeAPIView(APIView):
    """
    REST API endpoint for executing dataset recipes (parameterized SQL queries).

    URL: /api/workspace/<workspace_slug>/database/<db_name>/datasetrecipe/<recipe_id>/
    """

    # Support both session auth (web) and token auth (API)
    authentication_classes = [SessionAuthentication, WorkspaceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, workspace_slug, db_name):
        """
        POST endpoint to create a new dataset recipe.

        Request Body (JSON):
        - name: Recipe name (required)
        - sql_template: SQL query template with {{param}} placeholders (required)
        - description: Recipe description (optional)
        - parameters_schema: JSON schema for parameters (optional)
        - is_active: Whether the recipe is active (optional, default: true)
        """
        # Validate workspace access
        try:
            workspace = Workspace.objects.filter_for_user(request.user).get(slug=workspace_slug)
        except Workspace.DoesNotExist:
            return Response(
                {"error": "Workspace not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check permission to view database tables (reusing existing permission)
        if not view_database_tables(request.user, workspace):
            return Response(
                {"error": "Permission denied to create dataset recipes"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Verify database belongs to workspace
        if workspace.db_name != db_name:
            return Response(
                {"error": "Database does not belong to this workspace"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate request data
        serializer = RecipeCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        # Check if recipe with same name already exists in workspace
        if DatasetRecipe.objects.filter(workspace=workspace, name=validated_data["name"]).exists():
            return Response(
                {
                    "error": (
                        f"Recipe with name '{validated_data['name']}' "
                        "already exists in this workspace"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create the recipe
        recipe = DatasetRecipe.objects.create(
            workspace=workspace,
            name=validated_data["name"],
            description=validated_data.get("description", ""),
            sql_template=validated_data["sql_template"],
            parameters_schema=validated_data.get("parameters_schema", {}),
            is_active=validated_data.get("is_active", True),
            created_by=request.user,
            updated_by=request.user,
        )

        # Return created recipe details
        response_data = {
            "id": str(recipe.id),
            "name": recipe.name,
            "description": recipe.description,
            "sql_template": recipe.sql_template,
            "parameters_schema": recipe.parameters_schema,
            "is_active": recipe.is_active,
            "workspace": workspace_slug,
            "database": db_name,
            "created_at": recipe.created_at.isoformat(),
            "created_by": request.user.email if request.user else None,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    def patch(self, request, workspace_slug, db_name, recipe_id):
        """
        PATCH endpoint to update an existing dataset recipe.

        Request Body (JSON) - all fields optional:
        - name: Recipe name
        - sql_template: SQL query template with {{param}} placeholders
        - description: Recipe description
        - parameters_schema: JSON schema for parameters
        - is_active: Whether the recipe is active
        """
        # Validate workspace access
        try:
            workspace = Workspace.objects.filter_for_user(request.user).get(slug=workspace_slug)
        except Workspace.DoesNotExist:
            return Response(
                {"error": "Workspace not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check permission to view database tables (reusing existing permission)
        if not view_database_tables(request.user, workspace):
            return Response(
                {"error": "Permission denied to update dataset recipes"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Verify database belongs to workspace
        if workspace.db_name != db_name:
            return Response(
                {"error": "Database does not belong to this workspace"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch the recipe
        try:
            recipe = DatasetRecipe.objects.get(id=recipe_id, workspace=workspace)
        except DatasetRecipe.DoesNotExist:
            return Response(
                {"error": f"Recipe '{recipe_id!s}' not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validate request data (partial update, all fields optional)
        serializer = RecipeCreateUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        # Check if trying to rename to an existing recipe name
        if "name" in validated_data and validated_data["name"] != recipe.name:
            if DatasetRecipe.objects.filter(
                workspace=workspace, name=validated_data["name"]
            ).exists():
                return Response(
                    {
                        "error": (
                            f"Recipe with name '{validated_data['name']}' "
                            "already exists in this workspace"
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Update recipe fields
        if "name" in validated_data:
            recipe.name = validated_data["name"]
        if "description" in validated_data:
            recipe.description = validated_data["description"]
        if "sql_template" in validated_data:
            recipe.sql_template = validated_data["sql_template"]
        if "parameters_schema" in validated_data:
            recipe.parameters_schema = validated_data["parameters_schema"]
        if "is_active" in validated_data:
            recipe.is_active = validated_data["is_active"]

        recipe.updated_by = request.user
        recipe.save()

        # Return updated recipe details
        response_data = {
            "id": str(recipe.id),
            "name": recipe.name,
            "description": recipe.description,
            "sql_template": recipe.sql_template,
            "parameters_schema": recipe.parameters_schema,
            "is_active": recipe.is_active,
            "workspace": workspace_slug,
            "database": db_name,
            "created_at": recipe.created_at.isoformat(),
            "updated_at": recipe.updated_at.isoformat(),
            "created_by": recipe.created_by.email if recipe.created_by else None,
            "updated_by": request.user.email if request.user else None,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def get(self, request, workspace_slug, db_name, recipe_id=None):
        """
        GET endpoint to execute a dataset recipe with optional parameters and filters.

        Query Parameters:
        - format: Response format ('json' or 'csv', default: 'json')
        - limit: Optional limit on number of rows (default: from recipe schema)
        - Any recipe-specific parameters defined in the recipe's parameters_schema
        - Column filters using operators (e.g., date__gte=2024-01-01, status__eq=active)
          Supported operators: eq, neq, gt, gte, lt, lte, contains, icontains,
          startswith, endswith

        V1 Implementation: Filters are applied to the recipe result set.
        Works for single-table and multi-table (JOIN) queries.
        """
        # Validate workspace access
        try:
            workspace = Workspace.objects.filter_for_user(request.user).get(slug=workspace_slug)
        except Workspace.DoesNotExist:
            return Response(
                {"error": "Workspace not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check permission to view database tables
        if not view_database_tables(request.user, workspace):
            return Response(
                {"error": "Permission denied to view database tables"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Verify database belongs to workspace
        if workspace.db_name != db_name:
            return Response(
                {"error": "Database does not belong to this workspace"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch the recipe
        try:
            recipe = DatasetRecipe.objects.get(id=recipe_id, workspace=workspace, is_active=True)
        except DatasetRecipe.DoesNotExist:
            return Response(
                {"error": f"Recipe '{recipe_id!s}' not found or not active"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validate base query parameters
        serializer = RecipeExecuteSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        output_format = validated_data.get("format", "json")
        limit = validated_data.get("limit")

        # Reserved params that are not recipe parameters or filters
        reserved_params = {"format", "limit"}

        # Supported filter operators
        filter_operators = {
            "eq",
            "neq",
            "gt",
            "gte",
            "lt",
            "lte",
            "contains",
            "icontains",
            "startswith",
            "endswith",
        }

        # Separate recipe parameters from column filters
        recipe_params = {}
        column_filters = []

        for param_name, param_value in request.query_params.items():
            if param_name in reserved_params:
                continue

            # Check if this is a column filter (has __ operator)
            if "__" in param_name:
                column_name, operator = param_name.rsplit("__", 1)

                # If it's a valid filter operator, treat as column filter
                if operator in filter_operators:
                    column_filters.append(
                        {"column": column_name, "operator": operator, "value": param_value}
                    )
                    continue

            # Otherwise, treat as recipe parameter
            recipe_params[param_name] = param_value

        # Validate recipe parameters against schema
        try:
            validated_params = validate_recipe_parameters(recipe_params, recipe.parameters_schema)
        except ValueError as e:
            return Response(
                {"error": f"Parameter validation failed: {e!s}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Render the SQL template with parameters
        try:
            rendered_sql = render_recipe_sql(recipe.sql_template, validated_params)
        except Exception as e:
            return Response(
                {"error": f"SQL template rendering failed: {e!s}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Execute the query with filters
        try:
            data = execute_recipe_query(
                workspace, rendered_sql, limit=limit, column_filters=column_filters
            )
        except Exception as e:
            return Response(
                {"error": f"Query execution failed: {e!s}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Format response
        response_data = {
            "recipe_id": str(recipe.id),
            "recipe_name": recipe.name,
            "sql_template": recipe.sql_template,
            "rendered_sql": rendered_sql,
            "parameters": validated_params,
            "filters": column_filters,
            "data": data,
            "row_count": len(data),
            "workspace": workspace_slug,
            "database": db_name,
        }

        # Return response in requested format
        if output_format == "csv":
            if data:
                columns = list(data[0].keys())
                return self._generate_csv_response(data, columns)
            return Response(
                {"error": "No data to export as CSV"},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(response_data, status=status.HTTP_200_OK)

    def _generate_csv_response(self, data, columns):
        """Generate CSV response from recipe data."""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(data)

        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="recipe_data.csv"'
        return response
