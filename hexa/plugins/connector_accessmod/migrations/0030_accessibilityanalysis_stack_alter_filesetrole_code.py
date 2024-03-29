# Generated by Django 4.0.4 on 2022-05-04 10:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_accessmod", "0029_project_dem"),
    ]

    operations = [
        migrations.AddField(
            model_name="accessibilityanalysis",
            name="stack",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="connector_accessmod.fileset",
            ),
        ),
        migrations.AlterField(
            model_name="filesetrole",
            name="code",
            field=models.CharField(
                choices=[
                    ("BARRIER", "Barrier"),
                    ("CATCHMENT_AREAS", "Catchment Areas"),
                    ("COVERAGE", "Coverage"),
                    ("DEM", "Dem"),
                    ("FRICTION_SURFACE", "Friction Surface"),
                    ("GEOMETRY", "Geometry"),
                    ("HEALTH_FACILITIES", "Health Facilities"),
                    ("LAND_COVER", "Land Cover"),
                    ("MOVING_SPEEDS", "Moving Speeds"),
                    ("POPULATION", "Population"),
                    ("SLOPE", "Slope"),
                    ("TRANSPORT_NETWORK", "Transport Network"),
                    ("TRAVEL_TIMES", "Travel Times"),
                    ("WATER", "Water"),
                    ("STACK", "Stack"),
                ],
                max_length=50,
            ),
        ),
    ]
