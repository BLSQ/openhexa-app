# Generated by Django 3.2.7 on 2021-11-11 10:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_airflow", "0016_default_run_config"),
    ]

    operations = [
        migrations.AddField(
            model_name="cluster",
            name="auto_sync",
            field=models.BooleanField(default=True),
        ),
    ]
