from django.db import migrations, models


def shared_to_visibility(apps, schema_editor):
    Dataset = apps.get_model("datasets", "Dataset")
    Dataset.objects.filter(shared_with_organization=True).update(
        visibility="ORGANIZATION"
    )


def visibility_to_shared(apps, schema_editor):
    Dataset = apps.get_model("datasets", "Dataset")
    Dataset.objects.filter(visibility__in=["ORGANIZATION", "PUBLIC"]).update(
        shared_with_organization=True
    )


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0019_dataset_public_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataset",
            name="visibility",
            field=models.CharField(
                choices=[
                    ("WORKSPACE", "Workspace"),
                    ("ORGANIZATION", "Organization"),
                    ("PUBLIC", "Public"),
                ],
                default="WORKSPACE",
                max_length=20,
            ),
        ),
        migrations.RunPython(shared_to_visibility, visibility_to_shared),
        migrations.RemoveField(
            model_name="dataset",
            name="shared_with_organization",
        ),
    ]
