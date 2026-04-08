from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("webapps", "0013_add_show_powered_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="webapp",
            name="custom_domain",
            field=models.CharField(blank=True, max_length=253, null=True, unique=True),
        ),
    ]
