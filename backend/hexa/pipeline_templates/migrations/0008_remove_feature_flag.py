from django.db import migrations


def remove_feature_flag(apps, schema_editor):
    Feature = apps.get_model("user_management", "Feature")
    feature = Feature.objects.filter(code="pipeline_templates")
    assert feature.count() <= 1
    feature.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("pipeline_templates", "0007_pipelinetemplateversion_user_and_more"),
        ("user_management", "0020_user_analytics_enabled"),
    ]

    operations = [
        migrations.RunPython(remove_feature_flag),
    ]
