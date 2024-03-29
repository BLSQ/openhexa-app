# Generated by Django 4.1.3 on 2022-12-09 08:29

import uuid

from django.db import migrations, models

import hexa.pipelines.models


class Migration(migrations.Migration):
    dependencies = [
        ("pipelines", "0008_indexes_django_4"),
    ]

    operations = [
        migrations.CreateModel(
            name="Pipeline",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            bases=(hexa.pipelines.models.IndexableMixin, models.Model),
        ),
    ]
