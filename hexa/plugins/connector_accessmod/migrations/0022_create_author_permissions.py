from django.db import migrations

from hexa.user_management.models import PermissionMode


def forwards_func(apps, schema_editor):
    Project = apps.get_model("connector_accessmod", "Project")
    ProjectPermission = apps.get_model("connector_accessmod", "ProjectPermission")
    for project in Project.objects.all():
        ProjectPermission.objects.create(
            project=project, user=project.author, team=None, mode=PermissionMode.OWNER
        )


class Migration(migrations.Migration):
    dependencies = [
        ("connector_accessmod", "0021_permissions_next"),
    ]

    operations = [
        migrations.RunPython(forwards_func, migrations.RunPython.noop),
    ]
