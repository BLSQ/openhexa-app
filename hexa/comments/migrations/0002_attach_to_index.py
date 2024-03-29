# Generated by Django 3.2.6 on 2021-09-07 09:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0018_datasource_permission_link"),
        ("comments", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="comment",
            name="content_type",
        ),
        migrations.RemoveField(
            model_name="comment",
            name="object_id",
        ),
        migrations.AddField(
            model_name="comment",
            name="index",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to="catalog.index",
            ),
            preserve_default=False,
        ),
    ]
