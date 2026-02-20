from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("webapps", "0007_webapp_inheritance"),
    ]

    operations = [
        migrations.AddField(
            model_name="webapp",
            name="is_public",
            field=models.BooleanField(default=False),
        ),
    ]
