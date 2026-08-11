import secrets
from collections import defaultdict

import django.core.validators
from django.db import migrations, models
from slugify import slugify

SLUG_MAX_LENGTH = 255


def backfill_slugs(apps, schema_editor):
    """Give every existing saved query a slug unique within its workspace.

    Cannot reuse ``generate_saved_query_slug``: historical models carry no custom
    methods, and a per-row existence query would not see the slugs assigned
    earlier in this same pass anyway. Names are not unique per workspace today,
    so collisions are expected rather than exceptional.

    Only rows still holding the empty default are touched, which makes the
    migration safe to re-run.
    """
    SavedQuery = apps.get_model("data_studio", "SavedQuery")

    taken = defaultdict(set)
    for workspace_id, slug in SavedQuery.objects.exclude(slug="").values_list(
        "workspace_id", "slug"
    ):
        taken[workspace_id].add(slug)

    updated = []
    for saved_query in SavedQuery.objects.filter(slug=""):
        used = taken[saved_query.workspace_id]
        suffix = ""
        while True:
            slug = (
                slugify(saved_query.name[: SLUG_MAX_LENGTH - len(suffix)] + suffix)
                or "query"
            )
            if slug not in used:
                break
            suffix = "-" + secrets.token_hex(3)
        used.add(slug)
        saved_query.slug = slug
        updated.append(saved_query)

    # `updated_at` is auto_now, and listing only `slug` keeps it out of the
    # UPDATE: the default ordering is on that column, so writing it here would
    # reshuffle every user's saved-query list on deploy.
    SavedQuery.objects.bulk_update(updated, ["slug"], batch_size=500)


class Migration(migrations.Migration):
    dependencies = [
        ("data_studio", "0004_merge_20260731_2053"),
    ]

    operations = [
        migrations.AddField(
            model_name="savedquery",
            name="slug",
            field=models.CharField(
                default="",
                editable=False,
                max_length=SLUG_MAX_LENGTH,
                validators=[django.core.validators.validate_slug],
            ),
            preserve_default=False,
        ),
        migrations.RunPython(backfill_slugs, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="savedquery",
            constraint=models.UniqueConstraint(
                models.F("workspace_id"),
                models.F("slug"),
                name="unique_saved_query_slug_per_workspace",
            ),
        ),
    ]
