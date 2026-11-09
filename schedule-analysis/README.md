# Scheduled pipeline launch heatmap

Answers "how many pipelines start at each hour of the week, and where are the peaks".

## 1. Export the schedules from production (read-only, one query)

With psql (read replica if available):

    psql "$DATABASE_URL" -f export_scheduled_pipelines.sql
    # -> scheduled_pipelines.csv in the current directory

Or from inside the app container if psql is not available:

    python manage.py shell < export_scheduled_pipelines_django.py > scheduled_pipelines.csv

Both use the scheduler's own filters: schedule set, pipeline not deleted, workspace not archived.
No cron expansion happens on the server.

## 2. Render the heatmap locally

    uv run scheduled_pipelines_heatmap.py scheduled_pipelines.csv --tz Europe/Brussels

(`uv` installs croniter in a throwaway environment; alternatively `pip install croniter==6.0.0`
and run with python3.) Prints the busiest minutes and writes `scheduled_pipelines_heatmap.html`.

Useful flags:

- `--tz UTC` (default) or any IANA zone for display. Crons always run in UTC.
- `--weeks 8` expands 8 weeks and averages, so monthly schedules show up as fractions.
- `--start 2026-11-16` pins the week (must be a Monday); default is next Monday.
- `--include-frequent` keeps hourly-or-faster pipelines in the grid (they are listed separately by default).
- `--frequent-threshold 12` changes what counts as high-frequency (runs per day).
- `--top 50` lists more exact-minute slots.
