# Generated by Django 4.2.17 on 2024-12-20 13:05

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pipeline_templates", "0002_alter_pipelinetemplate_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="pipelinetemplate",
            options={"ordering": ["name"]},
        ),
    ]