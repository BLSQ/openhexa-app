# Generated by Django 4.0.4 on 2022-05-12 13:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_accessmod", "0038_alter_project_extent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="extent",
            field=models.TextField(default="[]"),
            preserve_default=False,
        ),
    ]
