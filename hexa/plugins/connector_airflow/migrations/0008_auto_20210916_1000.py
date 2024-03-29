# Generated by Django 3.2.6 on 2021-09-16 10:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_airflow", "0007_auto_20210914_1402"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="cluster",
            options={"ordering": ("name",), "verbose_name": "Airflow Cluster"},
        ),
        migrations.AlterModelOptions(
            name="dag",
            options={"ordering": ["dag_id"], "verbose_name": "DAG"},
        ),
        migrations.RenameField(
            model_name="dag",
            old_name="airflow_id",
            new_name="dag_id",
        ),
        migrations.AddField(
            model_name="dag",
            name="description",
            field=models.TextField(blank=True),
        ),
    ]
