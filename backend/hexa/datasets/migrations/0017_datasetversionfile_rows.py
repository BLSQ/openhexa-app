import numpy as np
from django.db import migrations, models, transaction


def update_dataset_samples_and_rows(apps, schema_editor):
    DatasetVersionFile = apps.get_model("datasets", "DatasetVersionFile")

    from django.conf import settings

    from hexa.datasets.queue import load_df

    queryset = DatasetVersionFile.objects.filter(rows__isnull=True).prefetch_related(
        "samples"
    )

    for version_file in queryset.iterator(chunk_size=1000):
        with transaction.atomic():
            version_file.filename = version_file.uri.split("/")[
                -1
            ]  # cannot read properties using apps.get_model
            df = load_df(version_file)
            version_file.rows = len(df.index)
            version_file.save(update_fields=["rows"])

            if not df.empty and len(df.index) < 50:
                sample = df.head(settings.WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE)
                sample = sample.replace({np.inf: "inf", -np.inf: "-inf"})
                sample = sample.to_dict(orient="records")
                for version_sample in version_file.samples.all():
                    version_sample.sample = sample
                    version_sample.save(update_fields=["sample"])


class Migration(migrations.Migration):
    # This migration might take minutes in heavy-filled environments:
    # Setting atomic to false prevents a giant DB transaction, avoiding long DB locks
    # Risk: if there is an error, db will be partially migrated, and migration will have to be launched again
    # (however, in this case, we are already filtering correctly migrated files with `.filter(rows__isnull=True)`)
    atomic = False

    dependencies = [
        ("datasets", "0016_add_shared_with_organization"),
    ]

    operations = [
        migrations.AddField(
            model_name="datasetversionfile",
            name="rows",
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.RunPython(
            update_dataset_samples_and_rows, migrations.RunPython.noop
        ),
    ]
