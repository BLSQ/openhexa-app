import django.db.models.deletion
from django.db import migrations, models

import hexa.plugins.connector_accessmod.models


def forward(apps, schema_editor):
    FilesetRole = apps.get_model("connector_accessmod", "FilesetRole")

    for name, code, format in [
        ("Boundaries", "BOUNDARIES", "VECTOR"),
        ("Zonal Statistics", "ZONAL_STATISTICS", "VECTOR"),
        ("Zonal Statistics Table", "ZONAL_STATISTICS_TABLE", "TABULAR"),
    ]:
        FilesetRole.objects.get_or_create(
            name=name, format=format, defaults={"code": code}
        )


class Migration(migrations.Migration):
    dependencies = [
        ("connector_accessmod", "0046_am_stack_priorities"),
    ]

    operations = [
        migrations.AlterField(
            model_name="filesetrole",
            name="code",
            field=models.CharField(
                choices=[
                    ("BARRIER", "Barrier"),
                    ("COVERAGE", "Coverage"),
                    ("DEM", "Dem"),
                    ("FRICTION_SURFACE", "Friction Surface"),
                    ("GEOMETRY", "Geometry"),
                    ("HEALTH_FACILITIES", "Health Facilities"),
                    ("LAND_COVER", "Land Cover"),
                    ("POPULATION", "Population"),
                    ("TRANSPORT_NETWORK", "Transport Network"),
                    ("TRAVEL_TIMES", "Travel Times"),
                    ("WATER", "Water"),
                    ("STACK", "Stack"),
                    ("BOUNDARIES", "Boundaries"),
                    ("ZONAL_STATISTICS", "Zonal Statistics"),
                    ("ZONAL_STATISTICS_TABLE", "Zonal Statistics Table"),
                ],
                max_length=50,
            ),
        ),
        migrations.CreateModel(
            name="ZonalStatisticsAnalysis",
            fields=[
                (
                    "analysis_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="connector_accessmod.analysis",
                    ),
                ),
                (
                    "time_thresholds",
                    models.JSONField(
                        default=hexa.plugins.connector_accessmod.models.get_default_time_thresholds
                    ),
                ),
                (
                    "boundaries",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="connector_accessmod.fileset",
                    ),
                ),
                (
                    "population",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="connector_accessmod.fileset",
                    ),
                ),
                (
                    "travel_times",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="connector_accessmod.fileset",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Zonal statistics",
            },
            bases=("connector_accessmod.analysis",),
        ),
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
