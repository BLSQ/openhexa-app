from django.db import migrations


def remove_feature_flag(apps, schema_editor):
    Feature = apps.get_model("user_management", "Feature")
    feature = Feature.objects.filter(code="datasets.smart_previewer")
    assert feature.count() <= 1
    feature.delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            "datasets",
            "0014_remove_feature_flag",
        ),
        ("user_management", "0021_remove_feature_flag"),
    ]

    operations = [
        migrations.RunPython(remove_feature_flag),
    ]
