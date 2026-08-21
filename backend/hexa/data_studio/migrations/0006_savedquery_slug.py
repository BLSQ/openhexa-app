import secrets

import django.core.validators
from django.db import migrations, models
from slugify import slugify

# Kept local rather than imported from the model: a migration must keep running
# against the schema it was written for, whatever the model says later.
SLUG_MAX_LENGTH = 255
SLUG_COLLISION_ATTEMPTS = 8


def backfill_slugs(apps, schema_editor):
    """Give every existing saved query a slug unique across all workspaces.

    Cannot reuse ``generate_saved_query_slug``: historical models carry no custom
    methods, and a per-row existence query would not see the slugs assigned
    earlier in this same pass anyway. Names are not unique today, so collisions
    are expected rather than exceptional.

    Each retry draws a fresh 6 hex-character suffix, so the attempt cap is never
    reached by chance; it is there so a broken run fails loudly instead of
    spinning inside a migration.

    Only rows still holding the empty default are touched, which makes the
    migration safe to re-run.
    """
    SavedQuery = apps.get_model("data_studio", "SavedQuery")

    taken = set(SavedQuery.objects.exclude(slug="").values_list("slug", flat=True))

    updated = []
    for saved_query in SavedQuery.objects.filter(slug=""):
        suffix = ""
        for _attempt in range(SLUG_COLLISION_ATTEMPTS):
            slug = (
                slugify(saved_query.name[: SLUG_MAX_LENGTH - len(suffix)] + suffix)
                or "query"
            )
            if slug not in taken:
                break
            suffix = "-" + secrets.token_hex(3)
        else:
            raise RuntimeError(
                f"Could not generate a unique slug for saved query {saved_query.pk} "
                f"in {SLUG_COLLISION_ATTEMPTS} attempts"
            )
        taken.add(slug)
        saved_query.slug = slug
        updated.append(saved_query)

    # `updated_at` is auto_now, and listing only `slug` keeps it out of the
    # UPDATE: the default ordering is on that column, so writing it here would
    # reshuffle every user's saved-query list on deploy.
    SavedQuery.objects.bulk_update(updated, ["slug"], batch_size=500)


class Migration(migrations.Migration):
    dependencies = [
        ("data_studio", "0005_savedquery_visibility_and_more"),
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
                fields=("slug",), name="unique_saved_query_slug"
            ),
        ),
    ]
