# Generated by Django 4.1.7 on 2023-07-05 18:09

import uuid

import django.contrib.postgres.fields.citext
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("workspaces", "0031_alter_connection_connection_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkspaceInvitation",
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
                (
                    "email",
                    django.contrib.postgres.fields.citext.CIEmailField(max_length=254),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("ADMIN", "Admin"),
                            ("EDITOR", "Editor"),
                            ("VIEWER", "Viewer"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("PENDING", "Pending"), ("ACCEPTED", "Accepted")],
                        default="PENDING",
                        max_length=50,
                    ),
                ),
                (
                    "invited_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]