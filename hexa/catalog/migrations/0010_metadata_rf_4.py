# Generated by Django 3.2.6 on 2021-08-25 08:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0009_enable_trgm"),
        ("connector_dhis2", "0014_metadata_rf_2"),
        ("connector_s3", "0020_metadata_rf_3"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Tag",
        ),
    ]
