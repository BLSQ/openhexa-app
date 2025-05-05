from django.db import migrations


def remove_feature_flag(apps, schema_editor):
    Feature = apps.get_model("user_management", "Feature")
    feature = Feature.objects.filter(code="pipeline_webhook")
    assert feature.count() <= 1
    feature.delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            "pipelines",
            "0058_remove_pipeline_unique_pipeline_code_per_workspace_and_more",
        ),
        ("user_management", "0020_user_analytics_enabled"),
    ]

    operations = [
        migrations.RunPython(remove_feature_flag),
    ]
