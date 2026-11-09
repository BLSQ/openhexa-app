#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["croniter==6.0.0"]
# ///
"""Expand the cron schedules exported from production into a week-of-launches heatmap.

Input: the CSV produced by export_scheduled_pipelines.sql (columns id, workspace, code,
name, schedule, ...). Output: a self-contained HTML page plus a short text summary.

    uv run scheduled_pipelines_heatmap.py scheduled_pipelines.csv --tz Europe/Brussels

Crons are expanded in UTC, exactly as pipelines_scheduler.py evaluates them, and only
converted to --tz for display. Pipelines firing more often than --frequent-threshold
runs per day (default: hourly or more) would flood every cell, so they are listed
separately and left out of the heatmap unless --include-frequent is given.
"""

import argparse
import csv
import html
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from croniter import croniter

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MAX_FIRES_PER_PIPELINE = 500_000
# Sequential blue ramp, steps 100 -> 700 (light mode: light = near zero).
RAMP = [
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
    "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b",
]
# Dark mode uses the same ramp reversed so "near zero" recedes toward the dark surface.
RAMP_DARK = list(reversed(RAMP[2:]))


@dataclass
class ScheduledPipeline:
    id: str
    workspace: str
    code: str
    name: str
    schedule: str
    fires: list[datetime] = field(default_factory=list)

    @property
    def label(self) -> str:
        return f"{self.workspace}/{self.code}"


def next_monday(today: date) -> date:
    return today + timedelta(days=(7 - today.weekday()) % 7 or 7)


def read_pipelines(path: Path) -> list[ScheduledPipeline]:
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        return [
            ScheduledPipeline(
                id=row["id"],
                workspace=row.get("workspace") or "?",
                code=row.get("code") or row["id"],
                name=row.get("name") or "",
                schedule=(row.get("schedule") or "").strip(),
            )
            for row in reader
        ]


def expand(pipeline: ScheduledPipeline, start: datetime, end: datetime) -> None:
    it = croniter(pipeline.schedule, start - timedelta(seconds=1))
    while True:
        fire = it.get_next(datetime)
        if fire >= end:
            return
        pipeline.fires.append(fire)
        if len(pipeline.fires) >= MAX_FIRES_PER_PIPELINE:
            return


def ramp_index(count: float, max_count: float, steps: int) -> int:
    if count <= 0 or max_count <= 0:
        return -1
    return min(steps - 1, int(count / max_count * steps))


def fmt(n: float) -> str:
    return str(int(n)) if float(n).is_integer() else f"{n:.1f}"


def build_html(
    *,
    pipelines: list[ScheduledPipeline],
    frequent: list[ScheduledPipeline],
    invalid: list[ScheduledPipeline],
    heat: dict[tuple[int, int], float],
    heat_members: dict[tuple[int, int], Counter],
    slots: list[tuple[tuple[int, int, int], float, Counter]],
    tz: str,
    start: date,
    weeks: int,
    frequent_included: bool,
    launches_per_week: float,
) -> str:
    max_count = max(heat.values(), default=0)
    cell_w, cell_h, left, top = 42, 38, 56, 28
    width = left + 24 * cell_w + 8
    height = top + 7 * cell_h + 8

    cells = []
    tips = {}
    for d in range(7):
        for h in range(24):
            count = heat.get((d, h), 0)
            idx = ramp_index(count, max_count, len(RAMP))
            level = f"l{idx}" if idx >= 0 else "l-"
            key = f"{d}-{h}"
            x, y = left + h * cell_w, top + d * cell_h
            label = (
                f'<text x="{x + cell_w / 2}" y="{y + cell_h / 2 + 4}" class="val {level}">{fmt(count)}</text>'
                if count
                else ""
            )
            cells.append(
                f'<g class="cell" data-key="{key}" tabindex="0" role="gridcell" '
                f'aria-label="{DAYS[d]} {h:02d}:00, {fmt(count)} launches">'
                f'<rect x="{x + 1}" y="{y + 1}" width="{cell_w - 2}" height="{cell_h - 2}" rx="4" class="fill {level}"/>'
                f"{label}</g>"
            )
            members = heat_members.get((d, h))
            if members:
                tips[key] = {
                    "title": f"{DAYS[d]} {h:02d}:00–{h:02d}:59 ({tz})",
                    "count": fmt(count),
                    "items": [f"{name} ×{fmt(n / weeks)}" if n != weeks else name for name, n in members.most_common(40)],
                    "more": max(0, len(members) - 40),
                }

    hour_labels = "".join(
        f'<text x="{left + h * cell_w + cell_w / 2}" y="{top - 10}" class="axis">{h:02d}</text>' for h in range(24)
    )
    day_labels = "".join(
        f'<text x="{left - 10}" y="{top + d * cell_h + cell_h / 2 + 4}" class="axis day">{DAYS[d]}</text>'
        for d in range(7)
    )
    legend_steps = "".join(f'<span class="swatch fill l{i}"></span>' for i in range(len(RAMP)))

    def table_rows(rows):
        return "".join(f"<tr>{''.join(f'<td>{c}</td>' for c in r)}</tr>" for r in rows)

    slot_rows = table_rows(
        [
            (
                f"{DAYS[d]} {h:02d}:{m:02d}",
                fmt(count),
                "<br>".join(html.escape(n) for n, _ in members.most_common()),
            )
            for (d, h, m), count, members in slots
        ]
    )
    freq_rows = table_rows(
        [
            (html.escape(p.label), html.escape(p.name), f"<code>{html.escape(p.schedule)}</code>", fmt(len(p.fires) / weeks / 7))
            for p in sorted(frequent, key=lambda p: -len(p.fires))
        ]
    )
    invalid_rows = table_rows(
        [(html.escape(p.label), f"<code>{html.escape(p.schedule)}</code>") for p in invalid]
    )
    grid_rows = table_rows(
        [(DAYS[d], *[fmt(heat.get((d, h), 0)) for h in range(24)]) for d in range(7)]
    )
    peak = slots[0] if slots else None
    peak_text = f"{DAYS[peak[0][0]]} {peak[0][1]:02d}:{peak[0][2]:02d}" if peak else "–"
    peak_count = fmt(peak[1]) if peak else "0"
    busiest_hour = max(heat.items(), key=lambda kv: kv[1], default=None)
    busiest_text = f"{DAYS[busiest_hour[0][0]]} {busiest_hour[0][1]:02d}:00" if busiest_hour else "–"
    window = f"{start.isoformat()} to {(start + timedelta(weeks=weeks) - timedelta(days=1)).isoformat()}"
    avg_note = f" Counts are averages per week over {weeks} weeks." if weeks > 1 else ""
    freq_note = (
        "High-frequency pipelines are included in the grid."
        if frequent_included
        else f"{len(frequent)} high-frequency pipeline(s) are left out of the grid and listed below."
    )

    light_css = "".join(f".l{i}{{--c:{c}}}" for i, c in enumerate(RAMP))
    dark_css = "".join(
        f".l{i}{{--c:{RAMP_DARK[min(i, len(RAMP_DARK) - 1)]}}}" for i in range(len(RAMP))
    )
    # Steps >= 400 (index 6) carry white labels; lighter steps use primary ink.
    label_ink_light = "".join(f".val.l{i}{{fill:#fff}}" for i in range(6, len(RAMP)))
    label_ink_dark = "".join(f".val.l{i}{{fill:#0b0b0b}}" for i in range(len(RAMP) - 4, len(RAMP)))

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pipeline launch heatmap</title>
<style>
:root {{
  --page:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#898781;
  --grid:#e1e0d9; --axis:#c3c2b7; --border:rgba(11,11,11,.10); --empty:#f0efec;
  --tip-bg:#0b0b0b; --tip-ink:#f0efec;
}}
{light_css}
{label_ink_light}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --page:#0d0d0d; --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,.10); --empty:#222220;
    --tip-bg:#f0efec; --tip-ink:#0b0b0b;
  }}
  :root:not([data-theme="light"]) {{ {dark_css} }}
  :root:not([data-theme="light"]) .val {{ fill:#fff }}
  :root:not([data-theme="light"]) {{ {label_ink_dark} }}
}}
* {{ box-sizing:border-box }}
body {{ margin:0; background:var(--page); color:var(--ink); font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }}
main {{ max-width:1180px; margin:0 auto; padding:24px 16px 48px; }}
h1 {{ font-size:20px; margin:0 0 4px }}
h2 {{ font-size:15px; margin:32px 0 8px }}
p.sub {{ color:var(--ink2); margin:0 0 20px }}
.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; margin-bottom:20px }}
.tile {{ background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:12px 14px }}
.tile .k {{ color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.04em }}
.tile .v {{ font-size:24px; font-weight:600; margin-top:2px }}
.tile .d {{ color:var(--ink2); font-size:12px }}
.card {{ background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:16px; overflow-x:auto }}
svg {{ display:block; min-width:{width}px }}
.axis {{ fill:var(--muted); font-size:11px; text-anchor:middle }}
.axis.day {{ text-anchor:end; font-size:12px }}
.fill {{ fill:var(--c, var(--empty)); stroke:var(--surface); stroke-width:2 }}
.fill.l- {{ fill:var(--empty) }}
.val {{ font-size:11px; text-anchor:middle; fill:var(--ink); pointer-events:none }}
.cell {{ cursor:default; outline:none }}
.cell:hover .fill, .cell:focus .fill {{ stroke:var(--ink); stroke-width:1.5 }}
.legend {{ display:flex; align-items:center; gap:8px; margin-top:12px; color:var(--ink2); font-size:12px }}
.legend .ramp {{ display:flex; gap:1px }}
.swatch {{ display:inline-block; width:18px; height:12px; border-radius:2px; background:var(--c) }}
#tip {{ position:fixed; z-index:9; display:none; max-width:360px; background:var(--tip-bg); color:var(--tip-ink);
  border-radius:6px; padding:8px 10px; font-size:12px; pointer-events:none; box-shadow:0 4px 16px rgba(0,0,0,.25) }}
#tip b {{ display:block; margin-bottom:4px }}
#tip ul {{ margin:4px 0 0; padding-left:16px; max-height:50vh; overflow:hidden }}
table {{ border-collapse:collapse; width:100%; font-size:13px }}
th, td {{ text-align:left; padding:6px 8px; border-bottom:1px solid var(--grid); vertical-align:top }}
th {{ color:var(--muted); font-weight:500; font-size:12px }}
td:nth-child(2) {{ white-space:nowrap }}
code {{ font-size:12px; background:var(--empty); padding:1px 4px; border-radius:3px }}
details summary {{ cursor:pointer; color:var(--ink2) }}
.grid-table td, .grid-table th {{ padding:3px 4px; text-align:right; font-variant-numeric:tabular-nums }}
.grid-table td:first-child, .grid-table th:first-child {{ text-align:left }}
</style>
</head>
<body>
<main>
<h1>Scheduled pipeline launches by hour of week</h1>
<p class="sub">{len(pipelines)} active scheduled pipelines, week of {window}, times in {html.escape(tz)}.{avg_note} {freq_note}</p>

<div class="tiles">
  <div class="tile"><div class="k">Scheduled pipelines</div><div class="v">{len(pipelines)}</div><div class="d">{len(frequent)} high-frequency, {len(invalid)} invalid cron</div></div>
  <div class="tile"><div class="k">Launches per week</div><div class="v">{fmt(launches_per_week)}</div><div class="d">excluding high-frequency: {fmt(sum(heat.values()))}</div></div>
  <div class="tile"><div class="k">Busiest hour</div><div class="v">{busiest_text}</div><div class="d">{fmt(busiest_hour[1]) if busiest_hour else 0} launches in that hour</div></div>
  <div class="tile"><div class="k">Busiest minute</div><div class="v">{peak_text}</div><div class="d">{peak_count} pipelines start at that exact minute</div></div>
</div>

<div class="card">
<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="grid" aria-label="Launches per hour of week">
{hour_labels}
{day_labels}
{''.join(cells)}
</svg>
<div class="legend"><span>0</span><span class="ramp">{legend_steps}</span><span>{fmt(max_count)} launches/hour</span><span style="margin-left:auto">Hover or focus a cell to list its pipelines</span></div>
</div>

<details style="margin-top:12px"><summary>Table view of the grid</summary>
<div class="card" style="margin-top:8px"><table class="grid-table"><thead><tr><th></th>{''.join(f'<th>{h:02d}</th>' for h in range(24))}</tr></thead><tbody>{grid_rows}</tbody></table></div>
</details>

<h2>Busiest exact minutes</h2>
<p class="sub">Pipelines that start at the same minute compete for the runner at once. Top {len(slots)} slots.</p>
<div class="card"><table><thead><tr><th>Slot</th><th>Launches</th><th>Pipelines</th></tr></thead><tbody>{slot_rows}</tbody></table></div>

<h2>High-frequency pipelines</h2>
<p class="sub">Running at least {{threshold}} times a day; they add a constant background load to every hour.</p>
<div class="card"><table><thead><tr><th>Pipeline</th><th>Name</th><th>Cron</th><th>Runs/day</th></tr></thead><tbody>{freq_rows or '<tr><td colspan="4">None</td></tr>'}</tbody></table></div>

<h2>Invalid cron expressions</h2>
<p class="sub">The scheduler logs an error and skips these.</p>
<div class="card"><table><thead><tr><th>Pipeline</th><th>Cron</th></tr></thead><tbody>{invalid_rows or '<tr><td colspan="2">None</td></tr>'}</tbody></table></div>
</main>
<div id="tip" role="tooltip"></div>
<script>
const TIPS = {json.dumps(tips)};
const tip = document.getElementById('tip');
function show(cell, ev) {{
  const t = TIPS[cell.dataset.key];
  if (!t) {{ tip.style.display = 'none'; return; }}
  const items = t.items.map(i => '<li>' + i.replace(/[&<>]/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;'}})[c]) + '</li>').join('');
  tip.innerHTML = '<b>' + t.title + ' · ' + t.count + ' launches</b><ul>' + items + '</ul>' + (t.more ? '<div>… and ' + t.more + ' more</div>' : '');
  tip.style.display = 'block';
  move(ev, cell);
}}
function move(ev, cell) {{
  let x, y;
  if (ev && ev.clientX !== undefined) {{ x = ev.clientX; y = ev.clientY; }}
  else {{ const r = cell.getBoundingClientRect(); x = r.right; y = r.top; }}
  const w = tip.offsetWidth, h = tip.offsetHeight;
  tip.style.left = Math.min(x + 14, window.innerWidth - w - 8) + 'px';
  tip.style.top = (y + 14 + h > window.innerHeight ? y - h - 8 : y + 14) + 'px';
}}
document.querySelectorAll('.cell').forEach(cell => {{
  cell.addEventListener('mouseenter', e => show(cell, e));
  cell.addEventListener('mousemove', e => move(e, cell));
  cell.addEventListener('mouseleave', () => tip.style.display = 'none');
  cell.addEventListener('focus', () => show(cell, null));
  cell.addEventListener('blur', () => tip.style.display = 'none');
}});
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", type=Path, help="CSV from export_scheduled_pipelines.sql")
    ap.add_argument("--out", type=Path, default=Path("scheduled_pipelines_heatmap.html"))
    ap.add_argument("--tz", default="UTC", help="IANA timezone for display (crons themselves run in UTC)")
    ap.add_argument("--start", type=date.fromisoformat, help="Monday the week starts on (default: next Monday)")
    ap.add_argument("--weeks", type=int, default=1, help="Weeks to expand; counts are averaged per week")
    ap.add_argument("--frequent-threshold", type=float, default=24, help="Runs/day from which a pipeline counts as high-frequency")
    ap.add_argument("--include-frequent", action="store_true", help="Keep high-frequency pipelines in the heatmap")
    ap.add_argument("--top", type=int, default=25, help="Number of busiest exact minutes to list")
    args = ap.parse_args()

    tz = ZoneInfo(args.tz)
    start_day = args.start or next_monday(date.today())
    if start_day.weekday() != 0:
        ap.error("--start must be a Monday")
    start = datetime.combine(start_day, time.min, tzinfo=timezone.utc)
    end = start + timedelta(weeks=args.weeks)

    all_pipelines = read_pipelines(args.csv)
    invalid = [p for p in all_pipelines if not croniter.is_valid(p.schedule)]
    valid = [p for p in all_pipelines if croniter.is_valid(p.schedule)]
    for p in valid:
        expand(p, start, end)

    frequent = [p for p in valid if len(p.fires) / args.weeks / 7 >= args.frequent_threshold]
    in_grid = valid if args.include_frequent else [p for p in valid if p not in frequent]

    heat: dict[tuple[int, int], float] = defaultdict(float)
    heat_members: dict[tuple[int, int], Counter] = defaultdict(Counter)
    minute_counts: dict[tuple[int, int, int], float] = defaultdict(float)
    minute_members: dict[tuple[int, int, int], Counter] = defaultdict(Counter)
    for p in in_grid:
        for fire in p.fires:
            local = fire.astimezone(tz)
            key = (local.weekday(), local.hour)
            heat[key] += 1 / args.weeks
            heat_members[key][p.label] += 1
            mkey = (local.weekday(), local.hour, local.minute)
            minute_counts[mkey] += 1 / args.weeks
            minute_members[mkey][p.label] += 1

    slots = sorted(
        ((k, c, minute_members[k]) for k, c in minute_counts.items()),
        key=lambda kv: (-kv[1], kv[0]),
    )[: args.top]
    launches_per_week = sum(len(p.fires) for p in valid) / args.weeks

    page = build_html(
        pipelines=valid,
        frequent=frequent,
        invalid=invalid,
        heat=heat,
        heat_members=heat_members,
        slots=slots,
        tz=args.tz,
        start=start_day,
        weeks=args.weeks,
        frequent_included=args.include_frequent,
        launches_per_week=launches_per_week,
    ).replace("{threshold}", fmt(args.frequent_threshold))
    args.out.write_text(page)

    print(f"{len(valid)} scheduled pipelines ({len(frequent)} high-frequency, {len(invalid)} invalid), "
          f"{fmt(launches_per_week)} launches/week, week of {start_day} in {args.tz}")
    print(f"\nBusiest exact minutes{' (high-frequency excluded)' if not args.include_frequent else ''}:")
    for (d, h, m), count, _ in slots[:10]:
        print(f"  {DAYS[d]} {h:02d}:{m:02d}  {fmt(count):>6}")
    if invalid:
        print("\nInvalid cron expressions:")
        for p in invalid:
            print(f"  {p.label}: {p.schedule!r}")
    print(f"\nWrote {args.out.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
