# Generated manually for PATHWAYS-615 migration

from django.db import migrations


def migrate_workspaces_to_organization(apps, schema_editor):
    Organization = apps.get_model("user_management", "Organization")
    Workspace = apps.get_model("workspaces", "Workspace")

    try:
        organization = Organization.objects.get(name="Bluesquare")

        workspaces_without_org = Workspace.objects.filter(organization__isnull=True)

        if workspaces_without_org.exists():
            count = workspaces_without_org.update(organization=organization)
            print(f"Assigned {count} workspaces to Bluesquare organization")
        else:
            print("All workspaces already have an organization assigned")
    except Organization.DoesNotExist:
        print("Bluesquare organization not found, skipping workspace migration")


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0048_workspace_organization"),
        ("user_management", "0028_migrate_users_to_bluesquare_organization"),
    ]

    operations = [
        migrations.RunPython(
            migrate_workspaces_to_organization, migrations.RunPython.noop
        ),
    ]
