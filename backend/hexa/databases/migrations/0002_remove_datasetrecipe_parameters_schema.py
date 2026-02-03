from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("databases", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="datasetrecipe",
            name="parameters_schema",
        ),
    ]
