from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0016_add_shared_with_organization"),
    ]

    operations = [
        migrations.AddField(
            model_name="datasetversionfile",
            name="rows",
            field=models.IntegerField(default=None, null=True),
        ),
    ]
