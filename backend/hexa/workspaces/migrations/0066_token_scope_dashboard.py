"""Ship a django-sql-dashboard view of the workspace token scope audit.

The audit answers a question people watch over weeks rather than read once, so it
gets a dashboard at /dashboard/workspace-token-scope/. Superuser-only: the rows
carry user emails and IPs.

Seeded as data so it exists on deploy without anyone assembling it by hand.
Re-running the migration replaces the queries, which is also how they get edited.

TODO (HEXA-1775): Remove once the analysis has been done
"""

from django.db import migrations

SLUG = "workspace-token-scope"

DESCRIPTION = """
Every workspace-token-authenticated GraphQL request, by how far it reached outside
the workspace its token was issued for. All panels cover the last 30 days.

- **out of scope** — reached another workspace with no route from the token's own.
  These break the day tokens are scoped.
- **cross reachable** — reached another workspace through an org-shared dataset, a
  dataset link or a pipeline template. These keep working.
- **in scope** — never left the token's workspace.
"""

WINDOW = "created_at > now() - interval '30 days'"

# Membership tokens are stable, so the fingerprint is the token. Identity tokens are
# minted per notebook session, so counting fingerprints would count sessions.
TOKEN_IDENTITY = """
    case
        when token_type = 'membership' then token_fingerprint
        else token_type || ':' || user_id::text || ':' || workspace_id::text
    end
"""

TOKENS = f"""
with tokens as (
    select {TOKEN_IDENTITY} as token,
           bool_or(verdict = 'OUT_OF_SCOPE') as breaks,
           bool_or(verdict = 'CROSS_REACHABLE') as reaches
    from workspaces_workspacetokenusage
    where {WINDOW}
    group by 1
),
totals as (
    select count(*) as tokens,
           count(*) filter (where breaks) as breaking,
           count(*) filter (where reaches and not breaks) as reaching
    from tokens
),
requests as (
    select count(*) as total,
           count(*) filter (where verdict = 'OUT_OF_SCOPE') as out_of_scope
    from workspaces_workspacetokenusage
    where {WINDOW}
)
"""


def share(part: str, whole: str) -> str:
    """A '12.3%%' string, doubled up because the dashboard reads %% as a placeholder."""
    return f"coalesce(to_char(100.0 * {part} / nullif({whole}, 0), 'FM990.0'), '0') || '%%'"


# The summary reads as one block rather than a row of boxes, so the headline numbers
# land together. Four leading spaces make it a markdown code block, which survives
# the widget's HTML sanitiser where a table would not.
SUMMARY = f"""
{TOKENS}
select '    active tokens              ' || lpad(t.tokens::text, 5) || chr(10) ||
       '    would break if scoped      ' || lpad(t.breaking::text, 5) ||
           '  (' || {share("t.breaking", "t.tokens")} || ')' || chr(10) ||
       '    cross-workspace but legal  ' || lpad(t.reaching::text, 5) ||
           '  (' || {share("t.reaching", "t.tokens")} || ')' || chr(10) ||
       chr(10) ||
       '    requests                   ' || lpad(r.total::text, 5) || chr(10) ||
       '    out-of-scope requests      ' || lpad(r.out_of_scope::text, 5) ||
           '  (' || {share("r.out_of_scope", "r.total")} || ')'
       as markdown
from totals t, requests r
"""

QUERIES = [
    SUMMARY,
    f"""
{TOKENS}
select breaking || ' of ' || tokens as big_number,
       'tokens would break if scoped' as label
from totals
""",
    f"""
{TOKENS}
select {share("breaking", "tokens")} as big_number,
       'of active tokens' as label
from totals
""",
    f"""
{TOKENS}
select {share("out_of_scope", "total")} as big_number,
       'of requests' as label
from requests
""",
    f"""
select to_char(date_trunc('day', created_at), 'Mon DD') as bar_label,
       count(*) as bar_quantity
from workspaces_workspacetokenusage
where {WINDOW} and verdict = 'OUT_OF_SCOPE'
group by date_trunc('day', created_at)
order by date_trunc('day', created_at)
""",
    f"""
select coalesce(o.name, 'No organization') as bar_label,
       count(*) filter (where u.verdict = 'OUT_OF_SCOPE') as bar_quantity
from workspaces_workspacetokenusage u
join workspaces_workspace w on w.id = u.workspace_id
left join identity_organization o on o.id = w.organization_id
where u.{WINDOW}
group by 1
order by 2 desc
""",
    f"""
select root_field as bar_label,
       count(*) as bar_quantity
from workspaces_workspacetokenusage u,
     jsonb_array_elements_text(u.root_fields) as root_field
where u.{WINDOW} and u.verdict = 'OUT_OF_SCOPE'
group by 1
order by 2 desc
limit 15
""",
    f"""
select left(u.token_fingerprint, 8) as token,
       u.token_type as type,
       usr.email as owner,
       w.slug as scoped_to,
       count(*) as out_of_scope_requests,
       count(distinct key) as workspaces_reached,
       max(u.created_at)::date as last_seen
from workspaces_workspacetokenusage u
join workspaces_workspace w on w.id = u.workspace_id
join identity_user usr on usr.id = u.user_id
left join lateral jsonb_object_keys(u.foreign_workspaces) as key on true
where u.{WINDOW} and u.verdict = 'OUT_OF_SCOPE'
group by 1, 2, 3, 4
order by 5 desc
limit 100
""",
    f"""
select coalesce(nullif(split_part(u.client, ' ', 1), ''), 'unknown') as client,
       count(*) filter (where u.verdict = 'OUT_OF_SCOPE') as out_of_scope,
       count(*) as requests
from workspaces_workspacetokenusage u
where u.{WINDOW}
group by 1
order by 3 desc
limit 20
""",
]


def create_dashboard(apps, schema_editor):
    Dashboard = apps.get_model("django_sql_dashboard", "Dashboard")
    DashboardQuery = apps.get_model("django_sql_dashboard", "DashboardQuery")

    dashboard, _ = Dashboard.objects.update_or_create(
        slug=SLUG,
        defaults={
            "title": "Workspace token scope (HEXA-1775)",
            "description": DESCRIPTION.strip(),
            "view_policy": "superuser",
            "edit_policy": "superuser",
        },
    )
    dashboard.queries.all().delete()
    for sql in QUERIES:
        DashboardQuery.objects.create(dashboard=dashboard, sql=sql.strip())


def delete_dashboard(apps, schema_editor):
    apps.get_model("django_sql_dashboard", "Dashboard").objects.filter(
        slug=SLUG
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0065_workspacetokenusage"),
        ("django_sql_dashboard", "0004_add_description_help_text"),
    ]

    operations = [migrations.RunPython(create_dashboard, delete_dashboard)]
