# Generated by Django 4.0.4 on 2022-04-26 09:50

import django.contrib.postgres.functions
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_accessmod", "0020_am_teams"),
    ]

    operations = [
        migrations.CreateModel(
            name="ValidateFilesetJob",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.contrib.postgres.functions.TransactionNow
                    ),
                ),
                (
                    "execute_at",
                    models.DateTimeField(
                        default=django.contrib.postgres.functions.TransactionNow
                    ),
                ),
                (
                    "priority",
                    models.IntegerField(
                        default=0,
                        help_text="Jobs with higher priority will be processed first.",
                    ),
                ),
                ("task", models.CharField(max_length=255)),
                ("args", models.JSONField()),
            ],
            options={
                "db_table": "connector_accessmod_validatefilesetjob",
            },
        ),
    ]
