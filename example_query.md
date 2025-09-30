# Database Query API Usage Examples

The new database query API allows you to filter and paginate table data in workspace databases. Here are some usage examples:

## Basic Query with Filters

```graphql
query {
  workspace(slug: "my-workspace") {
    database {
      table(name: "users") {
        query(
          filters: [
            { column: "active", operator: EQ, value: true },
            { column: "age", operator: GE, value: 18 }
          ],
          orderBy: "created_at",
          direction: DESC,
          page: 1,
          perPage: 20
        ) {
          pageNumber
          hasNextPage
          hasPreviousPage
          items
        }
      }
    }
  }
}
```

## Available Filter Operators

- `EQ` - Equals
- `NE` - Not equals  
- `LT` - Less than
- `LE` - Less than or equal
- `GT` - Greater than
- `GE` - Greater than or equal
- `LIKE` - SQL LIKE pattern matching
- `ILIKE` - Case-insensitive LIKE
- `IN` - Value is in a list
- `NOT_IN` - Value is not in a list
- `IS_NULL` - Value is null
- `IS_NOT_NULL` - Value is not null

## More Examples

### Filter by multiple values:
```graphql
{
  filters: [
    { column: "status", operator: IN, value: ["active", "pending"] }
  ]
}
```

### Check for null values:
```graphql
{
  filters: [
    { column: "deleted_at", operator: IS_NULL }
  ]
}
```

### Text search:
```graphql
{
  filters: [
    { column: "name", operator: ILIKE, value: "%john%" }
  ]
}
```

## Security Features

- Permission-based access: Users need `databases.view_database` permission for the workspace
- SQL injection protection: All column names and values are properly parameterized
- Input validation: Invalid operators, page numbers, and per_page values are handled gracefully
- Rate limiting: Per-page is capped at 100 items to prevent performance issues

## API Response Format

The query returns a paginated result with:
- `pageNumber`: Current page number
- `hasNextPage`: Boolean indicating if there are more pages
- `hasPreviousPage`: Boolean indicating if there are previous pages  
- `items`: Array of table rows as JSON objects