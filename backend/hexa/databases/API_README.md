# Database Table REST API

This REST API provides endpoints for querying workspace database tables with support for filtering, sorting, and pagination.

## Endpoint

```
GET /api/workspace/<workspace_slug>/database/<db_name>/table/<table_name>/
```

## Authentication

The API supports two authentication methods:

1. **Session Authentication** (for web browsers)
   - Authenticated users with workspace access

2. **Token Authentication** (for API clients)
   - Use workspace access tokens in the Authorization header
   - Format: `Authorization: Bearer <access_token>`
   - Tokens can be obtained from workspace membership settings

## Permissions

- Users must be members of the workspace to access its database tables
- All workspace roles (VIEWER, EDITOR, ADMIN) have access to query tables

## Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number for pagination |
| `limit` | integer | No | 10 | Number of results per page (max: 1000) |
| `sort` | string | No | - | Column name to sort by |
| `direction` | string | No | asc | Sort direction: `asc` or `desc` |
| `format` | string | No | json | Response format: `json` or `csv` |
| `<column_name>` | string | No | - | Filter by column value (equals) |
| `<column_name>__<operator>` | string | No | - | Filter with operator (see below) |

### Filter Operators

Use the format `column__operator=value` to apply different filter operations:

| Operator | SQL | Description | Example |
|----------|-----|-------------|---------|
| `eq` | `=` | Equal (default) | `city__eq=Brussels` or `city=Brussels` |
| `neq` | `!=` | Not equal | `city__neq=Brussels` |
| `gt` | `>` | Greater than | `temperature_celsius__gt=20` |
| `gte` | `>=` | Greater than or equal | `temperature_celsius__gte=20` |
| `lt` | `<` | Less than | `temperature_celsius__lt=10` |
| `lte` | `<=` | Less than or equal | `humidity_percent__lte=50` |
| `contains` | `LIKE` | Contains (case-sensitive) | `city__contains=Bru` |
| `icontains` | `ILIKE` | Contains (case-insensitive) | `city__icontains=bru` |
| `startswith` | `LIKE` | Starts with | `city__startswith=Bru` |
| `endswith` | `LIKE` | Ends with | `city__endswith=ssels` |

## Examples

### Basic Query

```bash
curl -X GET \
  "http://localhost:8000/api/workspace/my-workspace/database/mydb123/table/users/" \
  -H "Authorization: Bearer <your_access_token>"
```

### Pagination

```bash
curl -X GET \
  "http://localhost:8000/api/workspace/my-workspace/database/mydb123/table/users/?page=2&limit=25" \
  -H "Authorization: Bearer <your_access_token>"
```

### Filtering by Column

```bash
# Filter by single column
curl -X GET \
  "http://localhost:8000/api/workspace/my-workspace/database/mydb123/table/users/?country=Belgium" \
  -H "Authorization: Bearer <your_access_token>"

# Filter by multiple columns
curl -X GET \
  "http://localhost:8000/api/workspace/my-workspace/database/mydb123/table/users/?country=Belgium&status=active" \
  -H "Authorization: Bearer <your_access_token>"
```

### Sorting

```bash
# Sort ascending
curl -X GET \
  "http://localhost:8000/api/workspace/my-workspace/database/mydb123/table/users/?sort=created_at&direction=asc" \
  -H "Authorization: Bearer <your_access_token>"

# Sort descending
curl -X GET \
  "http://localhost:8000/api/workspace/my-workspace/database/mydb123/table/users/?sort=created_at&direction=desc" \
  -H "Authorization: Bearer <your_access_token>"
```

### Advanced Filtering with Operators

```bash
# Greater than or equal (numerical)
curl -X GET \
  "http://localhost:8000/api/workspace/my-workspace/database/mydb123/table/weather_forecast/?temperature_celsius__gte=20" \
  -H "Authorization: Bearer <your_access_token>"

# Less than (numerical)
curl -X GET \
  "http://localhost:8000/api/workspace/my-workspace/database/mydb123/table/weather_forecast/?humidity_percent__lt=50" \
  -H "Authorization: Bearer <your_access_token>"

# Range query (combining multiple operators)
curl -X GET \
  "http://localhost:8000/api/workspace/my-workspace/database/mydb123/table/weather_forecast/?temperature_celsius__gte=10&temperature_celsius__lte=25" \
  -H "Authorization: Bearer <your_access_token>"

# Contains (case-insensitive text search)
curl -X GET \
  "http://localhost:8000/api/workspace/my-workspace/database/mydb123/table/weather_forecast/?city__icontains=bru" \
  -H "Authorization: Bearer <your_access_token>"

# Not equal
curl -X GET \
  "http://localhost:8000/api/workspace/my-workspace/database/mydb123/table/weather_forecast/?weather_condition__neq=Rainy" \
  -H "Authorization: Bearer <your_access_token>"

# Starts with
curl -X GET \
  "http://localhost:8000/api/workspace/my-workspace/database/mydb123/table/weather_forecast/?city__startswith=Bru" \
  -H "Authorization: Bearer <your_access_token>"
```

### Combined Query with Multiple Filters

```bash
# Multiple conditions with operators
curl -X GET \
  "http://localhost:8000/api/workspace/my-workspace/database/mydb123/table/weather_forecast/?city=Brussels&temperature_celsius__gte=15&humidity_percent__lte=80&sort=date&direction=desc&limit=10" \
  -H "Authorization: Bearer <your_access_token>"
```

### CSV Export

```bash
curl -X GET \
  "http://localhost:8000/api/workspace/my-workspace/database/mydb123/table/users/?format=csv" \
  -H "Authorization: Bearer <your_access_token>" \
  -o users.csv
```

## Response Format (JSON)

```json
{
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "country": "Belgium",
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "country": "Belgium",
      "created_at": "2024-01-16T14:20:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_rows": 150,
    "total_pages": 15,
    "has_next": true,
    "has_previous": false
  },
  "columns": ["id", "name", "country", "created_at"],
  "table": "users",
  "workspace": "my-workspace",
  "database": "mydb123"
}
```

## Error Responses

### 400 Bad Request
- Invalid query parameters
- Invalid column name for filtering or sorting
- Database doesn't belong to workspace

```json
{
  "error": "Column 'invalid_column' does not exist in table"
}
```

### 403 Forbidden
- User is not authenticated
- User doesn't have permission to access the workspace

```json
{
  "error": "Permission denied to view database tables"
}
```

### 404 Not Found
- Workspace not found
- Table not found

```json
{
  "error": "Table 'nonexistent_table' not found"
}
```

### 500 Internal Server Error
- Database connection error
- Query execution error

```json
{
  "error": "Database query failed: <error details>"
}
```

## Notes

- Column names in filters and sort parameters must be alphanumeric with underscores
- All column filters use exact matching (case-sensitive)
- Maximum limit per request is 1000 rows
- CSV format returns the same data but as a downloadable CSV file
- The API uses parameterized queries to prevent SQL injection

## Getting Your Access Token

1. Navigate to your workspace settings
2. Go to the "Members" section
3. Find your membership entry
4. Copy your access token

Alternatively, workspace admins can generate tokens for service accounts or automated access.
