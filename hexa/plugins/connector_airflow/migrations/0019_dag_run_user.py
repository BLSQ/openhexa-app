# Generated by Django 3.2.7 on 2021-12-08 16:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("connector_airflow", "0018_dag_run_blank_config"),
    ]

    operations = [
        migrations.AddField(
            model_name="dagrun",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
