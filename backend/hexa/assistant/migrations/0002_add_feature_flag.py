from django.db import migrations


def add_assistant_feature_flag(apps, schema_editor):
    Feature = apps.get_model("user_management", "Feature")

    try:
        Feature.objects.get(code="assistant")
    except Feature.DoesNotExist:
        Feature.objects.create(code="assistant")


class Migration(migrations.Migration):
    dependencies = [
        ("assistant", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_assistant_feature_flag),
    ]
