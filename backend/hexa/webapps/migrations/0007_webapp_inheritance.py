import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("superset", "0001_initial"),
        ("webapps", "0006_merge_0004_webapp_type_0005_fix_slug_constraint"),
    ]

    operations = [
        migrations.CreateModel(
            name="SupersetWebapp",
            fields=[
                (
                    "webapp_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="webapps.webapp",
                    ),
                ),
                (
                    "superset_dashboard",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="webapp",
                        to="superset.supersetdashboard",
                    ),
                ),
            ],
            bases=("webapps.webapp",),
        ),
    ]
