# Generated by Django 4.0.4 on 2022-05-04 12:31

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("connector_accessmod", "0031_remove_accessibilityanalysis_catchment_areas"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="accessibilityanalysis",
            name="priority_land_cover",
        ),
        migrations.RemoveField(
            model_name="accessibilityanalysis",
            name="priority_roads",
        ),
    ]
