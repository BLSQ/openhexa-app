# Generated by Django 4.1.3 on 2022-12-14 12:39

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import hexa.core.models.behaviors


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("pipelines", "0009_pipeline"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="pipeline",
            options={"verbose_name": "Pipeline v2"},
        ),
        migrations.AddField(
            model_name="pipeline",
            name="config",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="pipeline",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="pipeline",
            name="entrypoint",
            field=models.CharField(default="", max_length=200),
        ),
        migrations.AddField(
            model_name="pipeline",
            name="name",
            field=models.CharField(default="", max_length=200, unique=True),
        ),
        migrations.AddField(
            model_name="pipeline",
            name="parameters",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="pipeline",
            name="schedule",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="pipeline",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="PipelineRun",
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
                ("run_id", models.CharField(max_length=200)),
                ("execution_date", models.DateTimeField()),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("success", "Success"),
                            ("running", "Running"),
                            ("failed", "Failed"),
                            ("queued", "Queued"),
                        ],
                        max_length=200,
                    ),
                ),
                ("duration", models.DurationField(null=True)),
                ("config", models.CharField(blank=True, max_length=200)),
                ("webhook_token", models.CharField(blank=True, max_length=200)),
                ("messages", models.JSONField(blank=True, default=list, null=True)),
                ("outputs", models.JSONField(blank=True, default=list, null=True)),
                ("run_logs", models.TextField(blank=True, null=True)),
                ("current_progress", models.PositiveSmallIntegerField(default=0)),
                (
                    "pipeline",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="pipelines.pipeline",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-execution_date",),
            },
            bases=(models.Model, hexa.core.models.behaviors.WithStatus),
        ),
    ]
