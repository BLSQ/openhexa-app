# Generated by Django 5.0.2 on 2024-02-20 12:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pipelines", "0033_alter_pipelinerun_trigger_mode"),
    ]

    operations = [
        migrations.AddField(
            model_name="pipeline",
            name="deleted",
            field=models.BooleanField(default=False),
        ),
    ]