# Generated by Django 4.0.2 on 2022-02-22 21:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_accessmod", "0010_analysis_finetuning_2"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="crs",
            field=models.PositiveIntegerField(default=4326),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="analysis",
            name="status",
            field=models.CharField(
                choices=[
                    ("DRAFT", "Draft"),
                    ("READY", "Ready"),
                    ("QUEUED", "Queued"),
                    ("RUNNING", "Running"),
                    ("SUCCESS", "Success"),
                    ("FAILED", "Failed"),
                ],
                default="DRAFT",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="filesetrole",
            name="code",
            field=models.CharField(
                choices=[
                    ("BARRIER", "Barrier"),
                    ("DEM", "Dem"),
                    ("FRICTION_SURFACE", "Friction Surface"),
                    ("GEOMETRY", "Geometry"),
                    ("HEALTH_FACILITIES", "Health Facilities"),
                    ("LAND_COVER", "Land Cover"),
                    ("MOVING_SPEEDS", "Moving Speeds"),
                    ("POPULATION", "Population"),
                    ("SLOPE", "Slope"),
                    ("TRANSPORT_NETWORK", "Transport Network"),
                    ("WATER", "Water"),
                ],
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="geographiccoverageanalysis",
            name="anisotropic",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="geographiccoverageanalysis",
            name="max_travel_time",
            field=models.IntegerField(default=360, null=True),
        ),
    ]
