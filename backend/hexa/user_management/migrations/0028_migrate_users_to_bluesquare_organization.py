# Generated manually for PATHWAYS-615 migration

from django.db import migrations


def migrate_users(apps, schema_editor):
    Organization = apps.get_model("user_management", "Organization")
    OrganizationMembership = apps.get_model("user_management", "OrganizationMembership")
    OrganizationMembershipRole = apps.get_model(
        "user_management", "OrganizationMembershipRole"
    )
    User = apps.get_model("user_management", "User")

    try:
        organization = Organization.objects.get(name="Bluesquare")

        memberships_to_create = [
            OrganizationMembership(
                organization=organization,
                user=user,
                role=OrganizationMembershipRole.MEMBER,
            )
            for user in User.objects.exclude(
                id__in=organization.members.values_list("id", flat=True)
            )
        ]
        if memberships_to_create:
            OrganizationMembership.objects.bulk_create(memberships_to_create)
            print(
                f"Added {len(memberships_to_create)} users to Bluesquare organization"
            )
        else:
            print("No users needed to be added to organizations")
    except Organization.DoesNotExist:
        print("Bluesquare organization not found, skipping user migration")


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0027_alter_organizationinvitation_workspace_invitations"),
    ]

    operations = [
        migrations.RunPython(migrate_users),
    ]
