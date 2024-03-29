# Generated by Django 4.1.3 on 2023-01-25 14:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0009_rename_workspaceconnection_connection_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="connection",
            name="connection_type",
            field=models.TextField(
                choices=[
                    ("S3", "S3 Bucket"),
                    ("GCS", "GCS Bucket"),
                    ("POSTGRESQL", "PostgreSQL DB"),
                    ("CUSTOM", "Custom"),
                    ("DHIS2", "DHIS2 Instance"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="connection",
            name="slug",
            field=models.CharField(max_length=100, validators=[]),
        ),
        migrations.AlterField(
            model_name="connectionfield",
            name="code",
            field=models.CharField(max_length=255, validators=[]),
        ),
    ]
