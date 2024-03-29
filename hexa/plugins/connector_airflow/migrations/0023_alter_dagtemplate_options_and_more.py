# Generated by Django 4.0 on 2022-01-14 15:44

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("connector_airflow", "0022_dagpermission_alter_dag_user_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="dagtemplate",
            options={"ordering": ["code"], "verbose_name": "DAGTemplate"},
        ),
        migrations.RenameField(
            model_name="dagtemplate",
            old_name="builder",
            new_name="code",
        ),
        migrations.RemoveField(
            model_name="dag",
            name="credentials",
        ),
        migrations.CreateModel(
            name="DAGAuthorizedDatasource",
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
                ("datasource_id", models.UUIDField()),
                (
                    "dag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="authorized_datasources",
                        to="connector_airflow.dag",
                    ),
                ),
                (
                    "datasource_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
