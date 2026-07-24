from django.db import migrations, models
from slugify import slugify


def backfill_slugs(apps, schema_editor):
    SavedQuery = apps.get_model("data_studio", "SavedQuery")
    used = {}
    for saved_query in SavedQuery.objects.order_by("created_at").iterator():
        workspace_slugs = used.setdefault(saved_query.workspace_id, set())
        base = slugify(saved_query.name) or "query"
        slug = base
        while slug in workspace_slugs:
            slug = f"{base}-{str(saved_query.id)[:6]}"
        workspace_slugs.add(slug)
        saved_query.slug = slug
        saved_query.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [
        ("data_studio", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="savedquery",
            name="slug",
            field=models.SlugField(default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="savedquery",
            name="is_public",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="savedquery",
            name="parameters",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.RunPython(backfill_slugs, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="savedquery",
            constraint=models.UniqueConstraint(
                fields=["workspace", "slug"],
                name="data_studio_ws_slug_unique",
            ),
        ),
        migrations.AddIndex(
            model_name="savedquery",
            index=models.Index(
                fields=["workspace", "slug"],
                name="data_studio_ws_slug_idx",
            ),
        ),
    ]
