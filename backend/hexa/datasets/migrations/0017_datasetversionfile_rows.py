import numpy as np
from django.db import migrations, models, transaction


def update_dataset_samples_and_rows(apps, schema_editor):
    DatasetVersionFile = apps.get_model("datasets", "DatasetVersionFile")
    DatasetFileSample = apps.get_model("datasets", "DatasetFileSample")

    from django.conf import settings

    from hexa.datasets.queue import load_df

    queryset = DatasetVersionFile.objects.prefetch_related("samples")

    files_to_update = []
    samples_to_update = []

    for version_file in queryset.iterator(chunk_size=1000):
        version_file.filename = version_file.uri.split("/")[-1] # cannot read properties using apps.get_model
        df = load_df(version_file)
        version_file.rows = len(df.index)
        files_to_update.append(version_file)

        for version_sample in version_file.samples.all():
            if not df.empty:
                sample = df.head(settings.WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE)
                sample = sample.replace({np.inf: "inf", -np.inf: "-inf"})
                version_sample.sample = sample.to_dict(orient="records")
            samples_to_update.append(version_sample)

    with transaction.atomic():
        if files_to_update:
            DatasetVersionFile.objects.bulk_update(
                files_to_update,
                ["rows"],
                batch_size=1000,
            )

        if samples_to_update:
            DatasetFileSample.objects.bulk_update(
                samples_to_update,
                ["sample"],
                batch_size=1000,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0016_add_shared_with_organization"),
    ]

    operations = [
        migrations.AddField(
            model_name="datasetversionfile",
            name="rows",
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.RunPython(update_dataset_samples_and_rows, migrations.RunPython.noop),
    ]
