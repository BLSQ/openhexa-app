import logging
import secrets

from django.db import migrations

logger = logging.getLogger(__name__)


def make_random_password(
    length=16,
    allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789",
):
    return "".join(secrets.choice(allowed_chars) for i in range(length))


def create_readonly_roles_for_existing_workspaces(apps, schema_editor):
    from hexa.databases.api import create_read_only_role

    Workspace = apps.get_model("workspaces", "Workspace")

    for workspace in Workspace.objects.filter(db_ro_password__isnull=True):
        try:
            ro_password = make_random_password(length=16)
            create_read_only_role(workspace.db_name, ro_password)
            workspace.db_ro_password = ro_password
            workspace.save(update_fields=["db_ro_password"])
            logger.info(f"Created read-only role for workspace {workspace.slug}")
        except Exception as e:
            logger.error(
                f"Failed to create read-only role for workspace {workspace.slug}: {e}"
            )


def reverse_migration(apps, schema_editor):
    Workspace = apps.get_model("workspaces", "Workspace")
    Workspace.objects.update(db_ro_password=None)


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0053_workspace_db_ro_password"),
    ]

    operations = [
        migrations.RunPython(
            create_readonly_roles_for_existing_workspaces,
            reverse_code=reverse_migration,
        ),
    ]
