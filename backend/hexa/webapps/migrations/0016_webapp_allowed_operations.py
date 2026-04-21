from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("webapps", "0015_make_subdomain_required"),
    ]

    operations = [
        migrations.AddField(
            model_name="webapp",
            name="allowed_operations",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
