from django.db import migrations


def remove_feature_flag(apps, schema_editor):
    Feature = apps.get_model("user_management", "Feature")
    feature = Feature.objects.filter(code="workspaces")
    assert feature.count() <= 1
    feature.delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            "workspaces",
            "0044_remove_workspaceinvitation_workspace_invitation_unique_workspace_email",
        ),
        ("user_management", "0020_user_analytics_enabled"),
    ]

    operations = [
        migrations.RunPython(remove_feature_flag),
    ]
