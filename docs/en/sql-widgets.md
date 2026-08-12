<div class="hero-section">
  <h1><i class="fas fa-chart-simple" style="margin-right: 0.5rem;"></i>SQL Chart Widgets</h1>
</div>

Data Studio draws a chart instead of a table when a query returns a specific set of column names: aliasing columns to `bar_label` and `bar_quantity` renders a bar chart, turning a saved query into a small dashboard.

The chart appears in a first tab and the usual tabular output stays in a second one, so nothing is hidden by charting a query.

## The conventions

| Chart | Columns to return | Use it for |
|-------|-------------------|------------|
| Bar | `bar_label`, `bar_quantity` | Comparing a measure across categories (districts, facilities, age groups) |
| Line | `line_x`, `line_y` | A trend over an ordered axis (months, weeks, epidemiological periods) |
| Pie | `pie_label`, `pie_quantity` | Part-to-whole, when there are only a few categories |

`*_label`, `*_x` are the text axis; `*_quantity`, `*_y` must hold numbers.

## Rules that decide whether a chart is drawn

The query must return the two columns of one chart. Extra columns are allowed: the chart ignores them and they stay readable in the table tab, so a query can keep an id or a filter column and still be drawn. If a query returns the columns of several charts at once, the first match wins, in the order bar, line, pie.

The value column must contain numbers. If it holds text, the result falls back to the table rather than drawing a misleading chart.

**Row order is the chart's order.** Charts never re-sort: they draw the rows in the order the query returned them. Always add an explicit `ORDER BY` — by value for a bar chart, by time for a line chart.

Aggregate before charting. A chart of ten thousand raw rows is unreadable, so `GROUP BY` the category and let the database do the counting. A bar chart shows at most 30 bars and a pie folds everything past the sixth slice into a single "Other" slice, so use `LIMIT` to keep the result to the categories that matter.

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

## When not to use a chart

Use a plain query when the user wants the records themselves, when they asked for a specific list of rows, or when the result has more than two meaningful columns. A chart answers "how does this compare?" or "how has this changed?" — not "show me the data".

Pie charts are the easiest to misuse: with more than about six categories, or with values that are close together, a bar chart is easier to read. Values must also be positive, since a slice represents a share of a whole; non-positive rows are left out of the pie.
