from django.db import migrations, models

import hexa.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0018_alter_datasetfilesample_dataset_version_file"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataset",
            name="public_slug",
            field=models.TextField(
                editable=False,
                max_length=255,
                null=True,
                unique=True,
                validators=[hexa.core.validators.validate_public_slug],
            ),
        ),
    ]
