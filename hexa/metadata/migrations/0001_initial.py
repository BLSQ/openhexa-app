# Generated by Django 4.2.16 on 2024-10-02 06:45

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="MetadataAttribute",
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
                ("object_id", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("key", models.CharField(max_length=255)),
                ("value", models.CharField(blank=True, max_length=255, null=True)),
                ("system", models.BooleanField(default=False)),
                (
                    "object_content_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["object_content_type", "object_id", "key"],
                        name="index_object_key",
                    )
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="metadataattribute",
            constraint=models.UniqueConstraint(
                fields=("object_content_type", "object_id", "key"),
                name="unique_key_per_data_object",
            ),
        ),
    ]