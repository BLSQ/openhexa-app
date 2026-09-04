<div class="hero-section">
  <h1><i class="fas fa-chart-simple" style="margin-right: 0.5rem;"></i>SQL Widgets</h1>
</div>

Data Studio draws a chart or a map instead of a table when a query returns a specific set of column names: `bar_label` and `bar_quantity` render a bar chart, `map_latitude` and `map_longitude` a map.

That turns a saved query into a small dashboard. The widget appears in a first tab and the usual tabular output stays in a second one, so nothing is hidden by charting or mapping a query.

## The conventions

| Chart | Columns to return | Use it for |
|-------|-------------------|------------|
| Bar | `bar_label`, `bar_quantity` | Comparing a measure across categories (districts, facilities, age groups) |
| Line | `line_x`, `line_y` | A trend over an ordered axis (months, weeks, epidemiological periods) |
| Pie | `pie_label`, `pie_quantity` | Part-to-whole, when there are only a few categories |
| Map | `map_latitude`, `map_longitude` | Places with known coordinates (facilities, households, survey points) |
| Map | `map_geometry` | Areas rather than points (districts, catchment areas, regions) |

`*_label`, `*_x` are the text axis; `*_quantity`, `*_y` must hold numbers. `map_latitude` and `map_longitude` must hold numbers in degrees, and `map_geometry` GeoJSON.

## Rules that decide whether a chart is drawn

The query must return the columns of one widget. Extra columns are allowed: a chart ignores them and they stay readable in the table tab, so a query can keep an id or a filter column and still be drawn. A map goes further and shows the extra columns in the popup of each feature, so name them the way you want them read. If a query returns the columns of several widgets at once, the first match wins, in the order bar, line, pie, map.

The value column must contain numbers. If it holds text, the result falls back to the table rather than drawing a misleading chart. The same applies to coordinates: a `map_latitude` outside -90..90 or a `map_longitude` outside -180..180 is not a location, and those rows are left off the map.

**Row order is the chart's order.** Charts never re-sort: they draw the rows in the order the query returned them. Always add an explicit `ORDER BY` — by value for a bar chart, by time for a line chart.

Aggregate before charting. A chart of ten thousand raw rows is unreadable, so `GROUP BY` the category and let the database do the counting. A bar chart shows at most 30 bars and a pie folds everything past the sixth slice into a single "Other" slice, so use `LIMIT` to keep the result to the categories that matter.

## Mapping

`map_latitude`/`map_longitude` is the simplest form and the one to prefer when the table already stores coordinates as numbers:

```sql
SELECT name, map_latitude, map_longitude FROM facilities;
```

For areas, convert the geometry to GeoJSON — a PostGIS geometry column returns binary WKB, which cannot be drawn:

```sql
SELECT district AS name, ST_AsGeoJSON(geom) AS map_geometry
FROM districts;
```

Forgetting `ST_AsGeoJSON` is the common mistake, and Data Studio says so in the map tab rather than falling back to the table silently.

Rows without a usable location are dropped from the map, and the map shows at most 2000 features — the table tab always holds the full result.

## Examples

Cases by district, largest first:

```sql
SELECT district AS bar_label, COUNT(*) AS bar_quantity
FROM cases
GROUP BY district
ORDER BY bar_quantity DESC
LIMIT 15;
```

Monthly trend for one region:

```sql
SELECT TO_CHAR(reported_on, 'YYYY-MM') AS line_x, COUNT(*) AS line_y
FROM cases
WHERE region = 'Northern'
GROUP BY line_x
ORDER BY line_x;
```

Share of confirmed cases by test type:

```sql
SELECT test_type AS pie_label, COUNT(*) AS pie_quantity
FROM cases
WHERE result = 'confirmed'
GROUP BY test_type
ORDER BY pie_quantity DESC;
```

Facilities of one region, with the columns that end up in each popup:

```sql
SELECT name, type, beds, map_latitude, map_longitude
FROM facilities
WHERE region = 'Northern';
```

## When not to use a widget

Use a plain query when the user wants the records themselves, when they asked for a specific list of rows, or when the result has more than two meaningful columns. A chart answers "how does this compare?" or "how has this changed?" — not "show me the data". A map answers "where?", so it is worth drawing only when the location is the point of the question.

Pie charts are the easiest to misuse: with more than about six categories, or with values that are close together, a bar chart is easier to read. Values must also be positive, since a slice represents a share of a whole; non-positive rows are left out of the pie.
