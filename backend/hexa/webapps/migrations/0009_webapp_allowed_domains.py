from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("webapps", "0008_webapp_is_public"),
    ]

    operations = [
        migrations.AddField(
            model_name="webapp",
            name="allowed_domains",
            field=models.TextField(blank=True, default=""),
        ),
    ]
