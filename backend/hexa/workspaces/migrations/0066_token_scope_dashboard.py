"""Ship a django-sql-dashboard view of the workspace token scope audit.
Superuser-only: the rows carry user emails and IPs.

Seeded as data so it exists on deploy without anyone assembling it by hand.
Re-running the migration replaces the queries, which is also how they get edited.
"""

from django.db import migrations

SLUG = "workspace-token-scope"

WINDOW = "created_at > now() - interval '30 days'"

# Membership tokens are stable, so the fingerprint is the token. Identity tokens
# are minted per notebook session, so counting fingerprints would count sessions.
TOKEN_IDENTITY = """
    case
        when token_type = 'membership' then token_fingerprint
        else token_type || ':' || user_id::text || ':' || workspace_id::text
    end
"""

ACTIVE_TOKENS = f"""
with tokens as (
    select {TOKEN_IDENTITY} as token,
           bool_or(verdict = 'OUT_OF_SCOPE') as breaks
    from workspaces_workspacetokenusage
    where {WINDOW}
    group by 1
)
"""

QUERIES = [
    """
select '## Workspace token scope audit

How far workspace-token-authenticated requests reach, relative to the workspace
their token was issued for. Instrumentation for HEXA-1775 — every panel covers the
last 30 days.

- **out of scope** — reached another workspace with no route from the token''s own.
  These break the day tokens are scoped.
- **cross reachable** — reached another workspace through an org-shared dataset, a
  dataset link or a pipeline template. These keep working.
- **in scope** — never left the token''s workspace.' as markdown
""",
    f"""
{ACTIVE_TOKENS}
select count(*) filter (where breaks) as big_number,
       'of ' || count(*) || ' active tokens would break if scoped' as label
from tokens
""",
    f"""
{ACTIVE_TOKENS}
select coalesce(round(100.0 * count(*) filter (where breaks) / nullif(count(*), 0)), 0) as big_number,
       '%% of active tokens reach outside their workspace' as label
from tokens
""",
    f"""
select count(*) filter (where verdict <> 'OUT_OF_SCOPE') as completed_count,
       count(*) as total_count
from workspaces_workspacetokenusage
where {WINDOW}
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
select coalesce(o.name, '—') as organization,
       count(*) filter (where u.verdict = 'OUT_OF_SCOPE') as out_of_scope,
       count(*) filter (where u.verdict = 'CROSS_REACHABLE') as cross_reachable,
       count(*) as requests
from workspaces_workspacetokenusage u
join workspaces_workspace w on w.id = u.workspace_id
left join identity_organization o on o.id = w.organization_id
where u.{WINDOW}
group by 1
order by 2 desc, 4 desc
""",
    f"""
select left(u.token_fingerprint, 8) as token,
       u.token_type,
       usr.email as owner,
       w.slug as scoped_to,
       count(*) as out_of_scope_requests,
       count(distinct key) as workspaces_reached,
       max(u.created_at) as last_seen
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
            "description": "Are workspace tokens used outside their workspace?",
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
