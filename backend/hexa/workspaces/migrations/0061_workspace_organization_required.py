import django.db.models.deletion
from django.db import migrations, models
from django.utils.text import slugify

DEFAULT_ORGANIZATION_NAME = "Default Organization"


def ensure_default_organization(apps, schema_editor):
    """Guarantee that at least one organization exists before making the
    workspace organization FK non-nullable.
    """
    Workspace = apps.get_model("workspaces", "Workspace")
    WorkspaceMembership = apps.get_model("workspaces", "WorkspaceMembership")
    Organization = apps.get_model("user_management", "Organization")
    OrganizationMembership = apps.get_model("user_management", "OrganizationMembership")
    User = apps.get_model("user_management", "User")

    orphans = Workspace.objects.filter(organization__isnull=True)
    orphan_ids = list(orphans.values_list("id", flat=True))
    if not orphan_ids and Organization.objects.exists():
        return

    organization, _ = Organization.objects.get_or_create(
        name=DEFAULT_ORGANIZATION_NAME,
        defaults={
            "slug": slugify(DEFAULT_ORGANIZATION_NAME),
            "organization_type": "CORPORATE",
        },
    )
    orphans.update(organization=organization)

    superuser_ids = set(
        User.objects.filter(is_superuser=True).values_list("id", flat=True)
    )
    workspace_admin_ids = set(
        WorkspaceMembership.objects.filter(
            workspace_id__in=orphan_ids, role="ADMIN"
        ).values_list("user_id", flat=True)
    )
    OrganizationMembership.objects.bulk_create(
        [
            OrganizationMembership(
                organization=organization, user_id=user_id, role="owner"
            )
            for user_id in superuser_ids
        ]
        + [
            OrganizationMembership(
                organization=organization, user_id=user_id, role="member"
            )
            for user_id in workspace_admin_ids - superuser_ids
        ],
        ignore_conflicts=True,
    )


def remove_default_organization(apps, schema_editor):
    Organization = apps.get_model("user_management", "Organization")
    OrganizationMembership = apps.get_model("user_management", "OrganizationMembership")

    default_organization = Organization.objects.filter(
        name=DEFAULT_ORGANIZATION_NAME, workspaces__isnull=True
    )
    assert default_organization.count() <= 1, "More than one default organization found"
    OrganizationMembership.objects.filter(
        organization__in=default_organization
    ).delete()
    default_organization.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0041_ensure_default_site"),
        ("workspaces", "0060_grant_create_on_public_to_rw_role"),
    ]

    operations = [
        migrations.RunPython(ensure_default_organization, remove_default_organization),
        migrations.AlterField(
            model_name="workspace",
            name="organization",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="workspaces",
                to="user_management.organization",
            ),
        ),
    ]
