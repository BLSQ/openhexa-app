# Generated by Django 4.0.4 on 2022-04-25 06:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "connector_accessmod",
            "0023_remove_project_project_unique_name_owner_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="fileset",
            name="metadata",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="fileset",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pending"),
                    ("VALID", "Valid"),
                    ("INVALID", "Invalid"),
                ],
                default="PENDING",
                max_length=50,
            ),
        ),
    ]
