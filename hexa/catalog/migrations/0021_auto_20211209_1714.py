# Generated by Django 3.2.7 on 2021-12-09 17:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0020_datasourcessyncjob"),
    ]

    operations = [
        migrations.AddField(
            model_name="index",
            name="datasource_id",
            field=models.UUIDField(null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="index",
            name="datasource_name",
            field=models.TextField(blank=True),
        ),
    ]
