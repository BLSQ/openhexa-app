# Generated by Django 4.0.4 on 2022-12-03 10:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_dhis2", "0030_remove_dataelement_collections_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="instance",
            name="start_synced_at",
            field=models.DateTimeField(null=True),
        ),
    ]
