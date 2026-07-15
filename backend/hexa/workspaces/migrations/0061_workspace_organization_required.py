import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q
from django.utils.text import slugify

DEFAULT_ORGANIZATION_NAME = "Default Organization"
MAX_NAME_ATTEMPTS = 10


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

    name = DEFAULT_ORGANIZATION_NAME
    slug = slugify(name)
    attempt = 1
    while Organization.objects.filter(Q(name=name) | Q(slug=slug)).exists():
        if attempt >= MAX_NAME_ATTEMPTS:
            raise RuntimeError(
                f"Could not find a free name for the default organization after "
                f"{MAX_NAME_ATTEMPTS} attempts"
            )
        attempt += 1
        name = f"{DEFAULT_ORGANIZATION_NAME} {attempt}"
        slug = slugify(name)

    organization = Organization.objects.create(
        name=name, slug=slug, organization_type="CORPORATE"
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
        ]
    )


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0041_ensure_default_site"),
        ("workspaces", "0060_grant_create_on_public_to_rw_role"),
    ]

    operations = [
        migrations.RunPython(ensure_default_organization, migrations.RunPython.noop),
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
