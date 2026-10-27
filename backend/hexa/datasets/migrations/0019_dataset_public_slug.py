import secrets

from django.db import migrations, models

# Frozen copy of hexa.datasets.models.RESERVED_PUBLIC_SLUGS at the time of this migration.
RESERVED_PUBLIC_SLUGS = {"new", "search", "create", "edit", "settings", "api"}


def backfill_public_slugs(apps, schema_editor):
    """Oldest datasets keep their workspace slug, later duplicates get a random suffix."""
    Dataset = apps.get_model("datasets", "Dataset")
    taken = set(RESERVED_PUBLIC_SLUGS)
    datasets = list(Dataset.objects.order_by("created_at", "id"))
    for dataset in datasets:
        suffix = ""
        while (slug := dataset.slug[: 255 - len(suffix)] + suffix) in taken:
            suffix = "-" + secrets.token_hex(3)
        taken.add(slug)
        dataset.public_slug = slug
    Dataset.objects.bulk_update(datasets, ["public_slug"], batch_size=1000)


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0018_alter_datasetfilesample_dataset_version_file"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataset",
            name="public_slug",
            field=models.TextField(editable=False, max_length=255, null=True),
        ),
        migrations.RunPython(backfill_public_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="dataset",
            name="public_slug",
            field=models.TextField(editable=False, max_length=255, unique=True),
        ),
    ]
