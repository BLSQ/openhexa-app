from django.db import migrations


def remove_feature_flag(apps, schema_editor):
    Feature = apps.get_model("user_management", "Feature")
    feature = Feature.objects.filter(code="search")
    assert feature.count() <= 1
    feature.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0021_remove_feature_flag"),
    ]

    operations = [
        migrations.RunPython(remove_feature_flag),
    ]
