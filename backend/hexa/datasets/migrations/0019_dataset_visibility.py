from django.db import migrations, models

PRIVATE = "PRIVATE"
ORGANIZATION = "ORGANIZATION"


def shared_flag_to_visibility(apps, schema_editor):
    Dataset = apps.get_model("datasets", "Dataset")
    Dataset.objects.filter(shared_with_organization=True).update(
        visibility=ORGANIZATION
    )


def visibility_to_shared_flag(apps, schema_editor):
    Dataset = apps.get_model("datasets", "Dataset")
    Dataset.objects.exclude(visibility=PRIVATE).update(shared_with_organization=True)


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0018_alter_datasetfilesample_dataset_version_file"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataset",
            name="visibility",
            field=models.CharField(
                choices=[
                    (PRIVATE, "Private"),
                    (ORGANIZATION, "Organization"),
                    ("PUBLIC", "Public"),
                ],
                default=PRIVATE,
                max_length=20,
            ),
        ),
        migrations.RunPython(shared_flag_to_visibility, visibility_to_shared_flag),
        migrations.RemoveField(
            model_name="dataset",
            name="shared_with_organization",
        ),
    ]
